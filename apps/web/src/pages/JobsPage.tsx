/**
 * Jobs list page: list current user's jobs with status.
 *
 * Context: This page lists all jobs for the current authenticated user. It is protected (e.g. by
 * PrivateRoute), so it is only visible when the user is logged in. useJobs fetches the list from
 * the API; useSession is used so the loading state reflects both session and jobs—JobsPageSkeleton
 * is shown when jobs are null or isLoading.
 *
 * If jobs is an empty list and not loading, the user is redirected to home. Each job is rendered
 * as a Cell: viewer on top, then title (localized "Untitled Gallery" when missing) and status
 * badge below; responsive grid size (12 on mobile, 6 on tablet, 4 on desktop). Clicking the Cell
 * navigates to the job page.
 */
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { Job } from "@geometry/domain";
import { Status } from "@geometry/domain";
import { Page, Container, Title, Badge, useDevice } from "@geometry/ui";
import { Viewer } from "@geometry/editor";
import { useJobs, useSession } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { Clock, TriangleAlert, CircleDotDashed, UserStar } from "lucide-react";
import { JobsPageSkeleton } from "../skeletons";
import { getDisplayStatus } from "../utils/jobStatus";

const VIEWER_HEIGHT = 250;

interface CellProps {
    job: Job;
}

const Cell = ({ job }: CellProps) => {
    const navigate = useNavigate();
    const { t } = useLocale();
    const { isMobile } = useDevice();
    const title =
        typeof job.meta?.title === "string" && job.meta.title.trim()
            ? String(job.meta.title)
            : t("editor.untitledGallery");
    const displayStatus = getDisplayStatus(job);
    const isSuccess = displayStatus === Status.SUCCESS && job.artGallery != null;
    const stitchedPointsCount = job.artGallery?.stitched?.points?.length ?? 0;
    const guardsCount = job.artGallery?.guards?.length ?? 0;

    return (
        <Container padded spaced rounded left pulse={displayStatus === Status.PENDING} onClick={() => navigate(`/jobs/${job.id}`)}>
            <Container size={12}>
                <Viewer artGallery={job.artGallery ?? undefined} size={VIEWER_HEIGHT} vertices />
            </Container>
            <Container size={isMobile ? 12 : 6} left>
                <Title left truncate>{title}</Title>
            </Container>
            <Container size={isMobile ? 12 : 6} right={!isMobile} center={isMobile}>
                <Title sm right={!isMobile} center={isMobile}>
                    <span className={`inline-flex items-center gap-1.5 ${isMobile ? "justify-center" : "justify-end"}`}>
                        <CircleDotDashed size={16} className="shrink-0 text-slate-600 dark:text-slate-400" aria-hidden />
                        {stitchedPointsCount}
                        <UserStar size={20} className="shrink-0 text-slate-600 dark:text-slate-400" aria-hidden />
                        {isSuccess ? guardsCount : (
                            <Badge danger={displayStatus === Status.FAILED}>
                                {displayStatus === Status.FAILED ? (
                                    <TriangleAlert size={16} aria-label={t(`jobs.status.${displayStatus}`)} />
                                ) : displayStatus === Status.PENDING ? (
                                    <Clock size={16} aria-label={t(`jobs.status.${displayStatus}`)} />
                                ) : (
                                    t(`jobs.status.${displayStatus}`)
                                )}
                            </Badge>
                        )}
                    </span>
                </Title>
            </Container>
        </Container>
    );
};

export const JobsPage = () => {
    const navigate = useNavigate();
    const { isMobile, isTablet } = useDevice();
    const { isLoading: sessionLoading } = useSession();
    const { jobs, isLoading: jobsLoading } = useJobs();
    const loading = sessionLoading || jobsLoading;

    useEffect(() => {
        if (!loading && jobs?.data?.length === 0) {
            navigate("/", { replace: true });
        }
    }, [loading, jobs?.data?.length, navigate]);

    if (jobs == null || loading) {
        return <JobsPageSkeleton />;
    }

    if (jobs.data.length === 0) {
        return null;
    }

    return (
        <Page>
            <Container spaced>
                {jobs.data.map((job) => (
                    <Container key={job.id} size={isMobile ? 12 : isTablet ? 6 : 4}>
                        <Cell job={job} />
                    </Container>
                ))}
            </Container>
        </Page>
    );
};
