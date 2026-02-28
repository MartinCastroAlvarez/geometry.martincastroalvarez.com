/**
 * Jobs list page: list current user's jobs with status.
 *
 * Context: This page lists all jobs for the current authenticated user. It is protected (e.g. by
 * PrivateRoute), so it is only visible when the user is logged in. useJobs fetches the list from
 * the API; useSession is used so the loading state reflects both session and jobs—JobsPageSkeleton
 * is shown until both are ready.
 *
 * The header shows a title ("My Jobs") and a count of jobs (or "Loading..." while fetching). Each
 * job is rendered as a link to /jobs/:id with a Button that displays a truncated job id and a
 * Badge for status (success or failed). Clicking a job navigates to JobPage for that id. If there
 * are no jobs, the list is simply empty.
 */
import { Link } from "react-router-dom";
import { Container, Title, Text, Button, Badge } from "@geometry/ui";
import { useJobs, useSession } from "@geometry/data";
import { WithJobsPageSkeleton } from "../skeletons";

export const JobsPage = () => {
    const { isLoading: sessionLoading } = useSession();
    const { jobs, isLoading: jobsLoading } = useJobs();
    const loading = sessionLoading || jobsLoading;

    return (
        <WithJobsPageSkeleton loading={loading}>
            <Container padded spaced>
            <Container center>
                <Title xl center>
                    My Jobs
                </Title>
                <Text center>
                    {jobsLoading ? "Loading..." : `${jobs?.data?.length ?? 0} job(s)`}
                </Text>
            </Container>
            {jobs?.data?.map((job) => (
                <Container key={job.id} padded spaced>
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
