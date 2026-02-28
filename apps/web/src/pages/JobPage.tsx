/**
 * Single job page: detail, title edit, publish/unpublish.
 *
 * Context: This page shows the detail view for one job, identified by the URL param :id. It is
 * protected (e.g. via PrivateRoute), so the user must be authenticated. useJob(id) fetches the job;
 * useSession is used to gate the loading state so we show JobPageSkeleton until both session and
 * job data are resolved.
 *
 * The page displays the job id (truncated), status (success/failed) as a Badge, and an editable
 * title input. The title is initialized from job.meta.title and persisted on blur via useUpdateJob.
 * Publish and Unpublish buttons are only rendered when job.status === "success"; they call
 * usePublish and useUnpublish with the job id. A "Back to Jobs" link navigates to the jobs list.
 * If the id param is missing, a short message is shown. Analytics: JOB_VIEW is tracked when the
 * job has loaded, with the job id as the label.
 */
import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Container, Title, Text, Button, Input, Badge } from "@geometry/ui";
import { useJob, usePublish, useUnpublish, useUpdateJob, useSession } from "@geometry/data";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { WithJobPageSkeleton } from "../skeletons";

export const JobPage = () => {
    const { id } = useParams<{ id: string }>();
    const { isLoading: sessionLoading } = useSession();
    const { job, isLoading: jobLoading } = useJob(id ?? null);
    const publish = usePublish();
    const unpublish = useUnpublish();
    const updateJob = useUpdateJob();
    const { track } = useAnalytics();
    const [title, setTitle] = useState("");
    useEffect(() => {
        if (job?.meta?.title != null) setTitle(String(job.meta.title));
    }, [job?.meta?.title]);
    useEffect(() => {
        if (id && !jobLoading && job) {
            track({
                action: GoogleAnalyticsActions.JOB_VIEW,
                category: GoogleAnalyticsCategories.PAGE,
                label: id,
            });
        }
    }, [id, jobLoading, job, track]);

    if (!id) return <Container padded spaced><Text>Job ID required</Text></Container>;

    const jobData = job!;
    const loading = sessionLoading || jobLoading || !job;
    const handlePublish = () => publish.mutate(id);
    const handleUnpublish = () => unpublish.mutate(id);
    const handleUpdateTitle = () => {
        if (title.trim() && id) updateJob.mutate({ jobId: id, meta: { title: title.trim() } });
    };

    return (
        <WithJobPageSkeleton loading={loading}>
            <Container padded spaced>
            <Container center>
                <Title xl center>
                    Job {jobData.id.slice(0, 12)}...
                </Title>
                <Badge danger={jobData.status === "failed"} success={jobData.status === "success"}>
                    {jobData.status}
                </Badge>
            </Container>
            <Container padded spaced>
                <Input
                    type="text"
                    placeholder="Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    onBlur={handleUpdateTitle}
                    className="max-w-md"
                />
            </Container>
            <Container padded spaced>
                {jobData.status === "success" && (
                    <>
                        <Button onClick={handlePublish} disabled={publish.isPending}>
                            {publish.isPending ? "Publishing..." : "Publish"}
                        </Button>
                        <Button onClick={handleUnpublish} disabled={unpublish.isPending}>
                            {unpublish.isPending ? "Unpublishing..." : "Unpublish"}
                        </Button>
                    </>
                )}
            </Container>
            <Container padded spaced>
                <Link to="/jobs">
                    <Button>Back to Jobs</Button>
                </Link>
            </Container>
            </Container>
        </WithJobPageSkeleton>
    );
};
