/**
 * Jobs list page: list current user's jobs with status.
 *
 * Context: useJobs fetches jobs from API; shows loading state and record count.
 * Each job is a Link to /jobs/:id with a Badge for status (success/failed).
 * Protected by PrivateRoute. Shows JobsPageSkeleton while session or jobs are loading.
 */
import { Link } from "react-router-dom";
import { Container, Title, Text, Button, Badge } from "@geometry/ui";
import { useJobs, useSession } from "@geometry/data";
import { WithJobsPageSkeleton } from "../skeletons";

export const JobsPage = () => {
    const { isLoading: sessionLoading } = useSession();
    const { jobs, isLoading: jobsLoading } = useJobs();

    return (
        <WithJobsPageSkeleton loading={sessionLoading || jobsLoading}>
            <Container padded spaced size={12}>
            <Container center>
                <Title xl center>
                    My Jobs
                </Title>
                <Text center>
                    {jobsLoading ? "Loading..." : `${jobs?.data.length ?? 0} job(s)`}
                </Text>
            </Container>
            {jobs?.data.map((job) => (
                <Container key={job.id} padded spaced size={12}>
                    <Link to={`/jobs/${job.id}`}>
                        <Button>
                            Job {job.id.slice(0, 8)}... <Badge danger={job.status === "failed"} success={job.status === "success"}>{job.status}</Badge>
                        </Button>
                    </Link>
                </Container>
            ))}
            </Container>
        </WithJobsPageSkeleton>
    );
};
