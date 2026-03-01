/**
 * Single job page: detail with title, status/step_name/created/updated badges, and stdin/stdout/stderr/meta inspectors.
 *
 * Context: This page shows the detail view for one job, identified by the URL param :id. It is
 * protected (e.g. via PrivateRoute). useJob(id) fetches the job; when loading and job is null,
 * JobPageSkeleton is shown. When not loading and job is null, redirect to home. Analytics: JOB_VIEW
 * is tracked when the job has loaded.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import { Page, Container, Title, Text, Badge, Badges, Inspector, Input, Toolbar, Button, Problem, Confirm, Milestones, Milestone, useDevice, useDebounce } from "@geometry/ui";
import { Viewer } from "@geometry/editor";
import { useJob, useJobChildren, useUpdateJob, usePublish, useSession } from "@geometry/data";
import { Status } from "@geometry/domain";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { useLocale } from "@geometry/i18n";
import { JobPageSkeleton } from "../skeletons";

const INSPECTOR_HEIGHT = 480;
const VIEWER_HEIGHT = 520;

export const JobPage = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { t } = useLocale();
    const { isMobile } = useDevice();
    const { isLoading: sessionLoading } = useSession();
    const { job, isLoading: jobLoading } = useJob(id ?? null);
    const childIds = job?.children_ids ?? [];
    const { children: childJobs, isLoading: childrenLoading } = useJobChildren(childIds.length ? childIds : null);
    const updateJobMutation = useUpdateJob();
    const publishMutation = usePublish();
    const { track } = useAnalytics();
    const [localTitle, setLocalTitle] = useState("");
    const hasInitializedTitle = useRef(false);
    const [showPublishConfirm, setShowPublishConfirm] = useState(false);
    const [publishError, setPublishError] = useState<string | undefined>(undefined);

    const loading = sessionLoading || jobLoading;

    useEffect(() => {
        if (!id) return;
        if (job && job.id === id && !hasInitializedTitle.current) {
            const title =
                typeof job.meta?.title === "string" && String(job.meta.title).trim()
                    ? String(job.meta.title)
                    : t("editor.untitledGallery");
            setLocalTitle(title);
            hasInitializedTitle.current = true;
        }
    }, [job, id, t]);

    useEffect(() => {
        hasInitializedTitle.current = false;
    }, [id]);

    const applyTitleUpdate = useCallback(
        (titleValue: string) => {
            if (!id) return;
            const value = titleValue.trim() || t("editor.untitledGallery");
            updateJobMutation.mutate(
                { jobId: id, meta: { title: value } },
                {
                    onSuccess: (data) => {
                        const next =
                            typeof data.meta?.title === "string" && String(data.meta.title).trim()
                                ? String(data.meta.title)
                                : t("editor.untitledGallery");
                        setLocalTitle(next);
                    },
                }
            );
        },
        [id, t, updateJobMutation]
    );

    const debouncedUpdateTitle = useDebounce(applyTitleUpdate, 400);

    useEffect(() => {
        if (id && !jobLoading && job) {
            track({
                action: GoogleAnalyticsActions.JOB_VIEW,
                category: GoogleAnalyticsCategories.PAGE,
                label: id,
            });
        }
    }, [id, jobLoading, job, track]);

    useEffect(() => {
        if (id && !sessionLoading && !jobLoading && job == null) {
            navigate("/", { replace: true });
        }
    }, [id, sessionLoading, jobLoading, job, navigate]);

    const handlePublishConfirm = useCallback(() => {
        setShowPublishConfirm(false);
        if (!id) return;
        publishMutation.mutate(id, {
            onError: (err) => setPublishError(err instanceof Error ? err.message : String(err)),
        });
    }, [id, publishMutation]);

    if (!id) {
        return (
            <Page>
                <Container padded spaced>
                    <Text>Job ID required</Text>
                </Container>
            </Page>
        );
    }

    if (loading && job == null) {
        return <JobPageSkeleton />;
    }

    if (publishMutation.isPending) {
        return <JobPageSkeleton />;
    }

    if (!loading && job == null) {
        return null;
    }

    const updatedLabel =
        job!.updated_at && !Number.isNaN(Date.parse(job!.updated_at))
            ? formatDistanceToNow(new Date(job!.updated_at), { addSuffix: true })
            : t("jobs.job.updated");

    const hasError = Object.keys(job!.stderr ?? {}).length > 0;

    return (
        <Page>
            <Container padded spaced>
                <Container
                    size={job!.status === Status.SUCCESS ? (isMobile ? 12 : 8) : 12}
                    left={!isMobile}
                    center={isMobile}
                >
                    <Input
                        type="text"
                        value={localTitle}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                            const v = e.target.value;
                            setLocalTitle(v);
                            debouncedUpdateTitle(v);
                        }}
                        placeholder={t("editor.untitledGallery")}
                        aria-label={t("editor.untitledGallery")}
                        className={isMobile ? "text-center max-w-full" : "text-left max-w-full"}
                        xl
                        transparent
                        strong
                    />
                </Container>
                {job!.status === Status.SUCCESS && (
                    <Container size={isMobile ? 12 : 4} center={isMobile} right={isMobile ? false : true}>
                        <Toolbar right={!isMobile} center={isMobile}>
                            <Button
                                onClick={() => {
                                    setPublishError(undefined);
                                    setShowPublishConfirm(true);
                                }}
                                sm
                                aria-label={t("jobs.job.publish")}
                            >
                                {t("jobs.job.publish")}
                            </Button>
                        </Toolbar>
                    </Container>
                )}
            </Container>
            <Confirm
                isOpen={showPublishConfirm}
                message={t("jobs.job.publishConfirm")}
                onConfirm={handlePublishConfirm}
                onCancel={() => setShowPublishConfirm(false)}
            />
            {publishError && (
                <Container padded spaced>
                    <Problem align="center">{publishError}</Problem>
                </Container>
            )}
            <Container padded spaced>
                <Container size={12} left={!isMobile} center={isMobile}>
                    <Badges left={!isMobile}>
                        <Badge danger={job!.status === Status.FAILED} success={job!.status === Status.SUCCESS}>
                            {t(`jobs.status.${job!.status}`)}
                        </Badge>
                        <Badge>
                            {t("jobs.job.updated")} {updatedLabel}
                        </Badge>
                    </Badges>
                </Container>
            </Container>
            {childIds.length > 0 && (
                <Container padded spaced>
                    <Container size={12} left center>
                        <Milestones>
                            {childrenLoading
                                ? childIds.map((_, i) => (
                                      <Milestone key={i} completed={false}>
                                          ...
                                      </Milestone>
                                  ))
                                : childJobs.map((child) => (
                                      <Milestone key={child.id} completed={child.status === Status.SUCCESS}>
                                          {child.step_name}
                                      </Milestone>
                                  ))}
                        </Milestones>
                    </Container>
                </Container>
            )}
            <Container padded spaced>
                <Viewer artGallery={job!.artGallery} height={VIEWER_HEIGHT} readonly fitToView />
            </Container>
            <Container padded spaced>
                <Container size={12} spaced>
                    <Container size={isMobile ? 12 : 4} left>
                        <Container left padded spaced>
                            <Title left>{t("jobs.job.input")}</Title>
                            <Inspector data={job!.stdin ?? {}} size={INSPECTOR_HEIGHT} />
                        </Container>
                    </Container>
                    <Container size={hasError ? 0 : isMobile ? 12 : 4} left>
                        <Container left padded spaced>
                            <Title left>{t("jobs.job.output")}</Title>
                            <Inspector data={job!.stdout ?? {}} size={INSPECTOR_HEIGHT} />
                        </Container>
                    </Container>
                    <Container size={hasError ? isMobile ? 12 : 4 : 0} left>
                        <Container left padded spaced>
                            <Title left>{t("jobs.job.error")}</Title>
                            <Inspector data={job!.stderr ?? {}} size={INSPECTOR_HEIGHT} />
                        </Container>
                    </Container>
                    <Container size={isMobile ? 12 : 4} left>
                        <Container left padded spaced>
                            <Title left>{t("jobs.job.metadata")}</Title>
                            <Inspector data={job!.meta ?? {}} size={INSPECTOR_HEIGHT} />
                        </Container>
                    </Container>
                </Container>
            </Container>
        </Page>
    );
};
