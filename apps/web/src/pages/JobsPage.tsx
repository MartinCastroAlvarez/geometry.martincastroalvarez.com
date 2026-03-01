/**
 * Jobs list page: list current user's jobs with status.
 *
 * Context: This page lists all jobs for the current authenticated user. It is protected (e.g. by
 * PrivateRoute), so it is only visible when the user is logged in. useJobs fetches the list from
 * the API; useSession is used so the loading state reflects both session and jobs—JobsPageSkeleton
 * is shown when jobs are null or isLoading.
 *
 * If jobs is an empty list and not loading, the user is redirected to home. Each job is rendered
 * as a Cell (title only, localized "Untitled Gallery" when missing) inside a Container with
 * responsive grid size (6 on mobile, 4 on tablet, 3 on desktop); clicking the Cell navigates to
 * the job page.
 */
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { Job } from "@geometry/domain";
import { Status } from "@geometry/domain";
import { Page, Container, Title, Badge, useDevice } from "@geometry/ui";
import { Viewer } from "@geometry/editor";
import { useJobs, useSession } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { JobsPageSkeleton } from "../skeletons";

const VIEWER_HEIGHT = 250;

interface CellProps {
    job: Job;
}

const Cell = ({ job }: CellProps) => {
    const navigate = useNavigate();
    const { t } = useLocale();
    const title =
        typeof job.meta?.title === "string" && job.meta.title.trim()
            ? String(job.meta.title)
            : t("editor.untitledGallery");

    return (
        <Container padded spaced rounded left onClick={() => navigate(`/jobs/${job.id}`)}>
            <Container size={8} left>
                <Title left truncate>{title}</Title>
            </Container>
            <Container size={4} right>
                <Badge danger={job.status === Status.FAILED} success={job.status === Status.SUCCESS}>
                    {t(`jobs.status.${job.status}`)}
                </Badge>
            </Container>
            <Container size={12}>
                <Viewer artGallery={job.artGallery ?? undefined} height={VIEWER_HEIGHT} readonly fitToView />
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
