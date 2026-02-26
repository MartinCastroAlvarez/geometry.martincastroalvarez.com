import { useParams, Link } from "react-router-dom";
import { Container, Title, Text, Button } from "@geometry/ui";
import { useJob, usePublish, useUnpublish, useUpdateJob } from "@geometry/data";
import { useState, useEffect } from "react";

export const JobPage = () => {
    const { id } = useParams<{ id: string }>();
    const { data: job, isLoading } = useJob(id ?? null);
    const publish = usePublish();
    const unpublish = useUnpublish();
    const updateJob = useUpdateJob();
    const [title, setTitle] = useState("");
    useEffect(() => {
        if (job?.meta?.title != null) setTitle(String(job.meta.title));
    }, [job?.meta?.title]);

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
                <Text center>Status: {job.status}</Text>
            </Container>
            <Container padded spaced size={12}>
                <input
                    type="text"
                    placeholder="Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    onBlur={handleUpdateTitle}
                    className="bg-x-surface text-x-text border border-x-border rounded-lg px-3 py-2 w-full max-w-md placeholder:text-x-text-muted focus:outline-none focus:border-x-text-muted"
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
