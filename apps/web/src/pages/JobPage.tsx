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
import { enUS, es } from "date-fns/locale";
import { Page, Container, Title, Text, Badge, Inspector, Input, Toolbar, Button, Problem, Confirm, Milestones, Milestone, MilestonesSkeleton, useDevice, useDebounce } from "@geometry/ui";
import { Viewer, Summary } from "@geometry/editor";
import { useJob, useJobChildren, useUpdateJob, usePublish, useDeleteJob, useReprocessJob, useSession, type ApiErrorResponse } from "@geometry/data";
import { Status } from "@geometry/domain";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { Language, useLocale } from "@geometry/i18n";
import { Pencil, RefreshCw, Trash2 } from "lucide-react";
import { JobPageSkeleton } from "../skeletons";
import { getDisplayStatus } from "../utils/jobStatus";

const INSPECTOR_HEIGHT = 480;
const VIEWER_HEIGHT = 520;

export const JobPage = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { t, language } = useLocale();
    const { isMobile } = useDevice();
    const { isLoading: sessionLoading } = useSession();
    const { job, isLoading: jobLoading } = useJob(id ?? null);
    const childIds = job?.children_ids ?? [];
    const { children: childJobs, isLoading: childrenLoading } = useJobChildren(childIds.length ? childIds : null);
    const updateJobMutation = useUpdateJob();
    const publishMutation = usePublish();
    const deleteJobMutation = useDeleteJob();
    const reprocessJobMutation = useReprocessJob();
    const { track } = useAnalytics();
    const [localTitle, setLocalTitle] = useState("");
    const hasInitializedTitle = useRef(false);
    const jobStatusRef = useRef<string | undefined>(undefined);
    const [showPublishConfirm, setShowPublishConfirm] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [showReprocessConfirm, setShowReprocessConfirm] = useState(false);
    const [publishError, setPublishError] = useState<string | undefined>(undefined);
    const [deleteError, setDeleteError] = useState<string | undefined>(undefined);
    const [reprocessError, setReprocessError] = useState<string | undefined>(undefined);

    const loading = sessionLoading || jobLoading;

    useEffect(() => {
        if (job) jobStatusRef.current = job.status;
    }, [job]);

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
                { jobId: id, meta: { title: value }, status: jobStatusRef.current },
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
            onSuccess: () => navigate("/"),
            onError: (error: Error & { apiError?: ApiErrorResponse["error"] }) => {
                const msg =
                    error.apiError?.type === "GalleryHasNoStitchesError"
                        ? t("errors.publishNoStitches")
                        : t("errors.publishFailed");
                setPublishError(msg);
            },
        });
    }, [id, publishMutation, navigate, t]);

    const handleTitleChange = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const v = e.target.value;
            setLocalTitle(v);
            debouncedUpdateTitle(v);
        },
        [debouncedUpdateTitle]
    );

    const handleEditClick = useCallback(() => {
        const copyOfPrefix = t("editor.copyOf");
        const trimmed = (localTitle ?? "").trimStart();
        const alreadyCopyOf =
            copyOfPrefix.length > 0 &&
            trimmed.toLowerCase().startsWith(copyOfPrefix.trim().toLowerCase());
        const titleForEditor = alreadyCopyOf ? localTitle : copyOfPrefix + (localTitle ?? "").trim();
        navigate("/design", {
            state: { artGallery: job?.artGallery, title: titleForEditor },
        });
    }, [navigate, job, localTitle, t]);

    const handlePublishClick = useCallback(() => {
        setPublishError(undefined);
        setShowPublishConfirm(true);
    }, []);

    const handlePublishConfirmCancel = useCallback(() => setShowPublishConfirm(false), []);

    const handleDeleteClick = useCallback(() => {
        setDeleteError(undefined);
        setShowDeleteConfirm(true);
    }, []);
    const handleDeleteConfirmCancel = useCallback(() => setShowDeleteConfirm(false), []);
    const handleDeleteConfirm = useCallback(() => {
        setShowDeleteConfirm(false);
        if (!id) return;
        deleteJobMutation.mutate(id, {
            onSuccess: () => navigate("/jobs"),
            onError: () => setDeleteError(t("errors.deleteFailed")),
        });
    }, [id, deleteJobMutation, navigate, t]);

    const handleReprocessClick = useCallback(() => {
        setReprocessError(undefined);
        setShowReprocessConfirm(true);
    }, []);
    const handleReprocessConfirmCancel = useCallback(() => setShowReprocessConfirm(false), []);
    const handleReprocessConfirm = useCallback(() => {
        setShowReprocessConfirm(false);
        if (!id) return;
        reprocessJobMutation.mutate(id, {
            onSuccess: () => {
                // useReprocessJob invalidates JOB_QUERY_KEY(id), so useJob will refetch
            },
            onError: () => setReprocessError(t("errors.reprocessFailed")),
        });
    }, [id, reprocessJobMutation, t]);

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

    if (publishMutation.isPending || deleteJobMutation.isPending || reprocessJobMutation.isPending) {
        return <JobPageSkeleton />;
    }

    if (!loading && job == null) {
        return null;
    }

    const dateFnsLocale = language === Language.ES ? es : enUS;
    const updatedLabel =
        job!.updated_at && !Number.isNaN(Date.parse(job!.updated_at))
            ? `${t("jobs.job.updated")} ${formatDistanceToNow(new Date(job!.updated_at), { addSuffix: true, locale: dateFnsLocale })}`
            : t("jobs.job.updated");

    const hasError = Object.keys(job!.stderr ?? {}).length > 0;
    const displayStatus = getDisplayStatus(job!);

    return (
        <Page>
            <Confirm
                isOpen={showPublishConfirm}
                message={t("jobs.job.publishConfirm")}
                onConfirm={handlePublishConfirm}
                onCancel={handlePublishConfirmCancel}
            />
            <Confirm
                isOpen={showDeleteConfirm}
                message={t("jobs.job.deleteConfirm")}
                onConfirm={handleDeleteConfirm}
                onCancel={handleDeleteConfirmCancel}
            />
            <Confirm
                isOpen={showReprocessConfirm}
                message={t("jobs.job.reprocessConfirm")}
                onConfirm={handleReprocessConfirm}
                onCancel={handleReprocessConfirmCancel}
            />
            {displayStatus === Status.SUCCESS && job!.artGallery != null ? (
                <Container padded spaced>
                    <Container size={12} left center>
                        <Summary artGallery={job!.artGallery} />
                    </Container>
                </Container>
            ) : childIds.length > 0 ? (
                <Container padded spaced>
                    <Container size={12} left center>
                        {childrenLoading ? (
                            <MilestonesSkeleton />
                        ) : (
                            <Milestones>
                                {childJobs.map((child) => (
                                    <Milestone key={child.id} completed={child.status === Status.SUCCESS}>
                                        {t(`jobs.steps.${child.step_name.replace(/-/g, "_")}`) || child.step_name}
                                    </Milestone>
                                ))}
                            </Milestones>
                        )}
                    </Container>
                </Container>
            ) : null}
            <Container padded spaced>
                <Viewer artGallery={job!.artGallery} size={VIEWER_HEIGHT} interactive />
            </Container>
            <Container padded spaced>
                <Container size={isMobile ? 12 : 6} left={!isMobile} center={isMobile}>
                    <Container size={12} left={!isMobile} center={isMobile}>
                        <Input
                            type="text"
                            value={localTitle}
                            onChange={handleTitleChange}
                            placeholder={t("editor.untitledGallery")}
                            aria-label={t("editor.untitledGallery")}
                            className={isMobile ? "text-center max-w-full" : "text-left max-w-full"}
                            xl
                            transparent
                            strong
                            readOnly={displayStatus !== Status.SUCCESS}
                        />
                    </Container>
                    <Container spaced>
                        <Container size={12} left={!isMobile} center={isMobile}>
                            <Text muted xxs left={!isMobile} center={isMobile}>
                                {updatedLabel}
                            </Text>
                        </Container>
                        {displayStatus !== Status.SUCCESS && (
                            <Container size={12} left={!isMobile}>
                                <Badge danger={displayStatus === Status.FAILED}>
                                    {t(`jobs.status.${displayStatus}`)}
                                </Badge>
                            </Container>
                        )}
                    </Container>
                </Container>
                <Container size={isMobile ? 12 : 6} center={isMobile} right={!isMobile}>
                    {(publishError || deleteError || reprocessError) && (
                        <Problem align={isMobile ? "center" : ("right" as const)} className="mb-2">
                            {publishError ?? deleteError ?? reprocessError}
                        </Problem>
                    )}
                    <Toolbar right={!isMobile} center={isMobile}>
                        {displayStatus === Status.SUCCESS && (
                            <Button
                                onClick={handlePublishClick}
                                primary
                                sm
                                aria-label={t("jobs.job.publish")}
                            >
                                {t("jobs.job.publish")}
                            </Button>
                        )}
                        <Button
                            onClick={handleReprocessClick}
                            icon={<RefreshCw size={16} aria-hidden />}
                            sm
                            aria-label={t("jobs.job.reprocess")}
                        />
                        {job!.artGallery != null && (
                            <Button
                                onClick={handleEditClick}
                                icon={<Pencil size={16} aria-hidden />}
                                sm
                                aria-label={t("jobs.job.edit")}
                            />
                        )}
                        <Button
                            onClick={handleDeleteClick}
                            icon={<Trash2 size={16} aria-hidden />}
                            sm
                            aria-label={t("jobs.job.delete")}
                        />
                    </Toolbar>
                </Container>
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
