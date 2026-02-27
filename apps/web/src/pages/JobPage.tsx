/**
 * Single job page: detail, title edit, publish/unpublish.
 *
 * Context: useJob(id) loads job; usePublish/useUnpublish/useUpdateJob for mutations.
 * Title is synced from job.meta.title and saved on blur. Publish/Unpublish only
 * when job.status === "success". Protected by PrivateRoute.
 */
import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Container, Title, Text, Button, Input, Badge } from "@geometry/ui";
import { useJob, usePublish, useUnpublish, useUpdateJob } from "@geometry/data";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";

export const JobPage = () => {
    const { id } = useParams<{ id: string }>();
    const { data: job, isLoading } = useJob(id ?? null);
    const publish = usePublish();
    const unpublish = useUnpublish();
    const updateJob = useUpdateJob();
    const { track } = useAnalytics();
    const [title, setTitle] = useState("");
    useEffect(() => {
        if (job?.meta?.title != null) setTitle(String(job.meta.title));
    }, [job?.meta?.title]);
    useEffect(() => {
        if (id && !isLoading && job) {
            track({
                action: GoogleAnalyticsActions.JOB_VIEW,
                category: GoogleAnalyticsCategories.PAGE,
                label: id,
            });
        }
    }, [id, isLoading, job, track]);

    if (!id) return <Text>Job ID required</Text>;
    if (isLoading || !job) return <Text>Loading...</Text>;

    const handlePublish = () => publish.mutate(id);
    const handleUnpublish = () => unpublish.mutate(id);
    const handleUpdateTitle = () => {
        if (title.trim()) updateJob.mutate({ jobId: id, meta: { title: title.trim() } });
    };

    return (
        <Container padded spaced size={12}>
            <Container center>
                <Title xl center>
                    Job {job.id.slice(0, 12)}...
                </Title>
                <Badge danger={job.status === "failed"} success={job.status === "success"}>
                    {job.status}
                </Badge>
            </Container>
            <Container padded spaced size={12}>
                <Input
                    type="text"
                    placeholder="Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    onBlur={handleUpdateTitle}
                    className="max-w-md"
                />
            </Container>
            <Container padded spaced size={12}>
                {job.status === "success" && (
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
            <Container padded spaced size={12}>
                <Link to="/jobs">
                    <Button>Back to Jobs</Button>
                </Link>
            </Container>
        </Container>
    );
};
