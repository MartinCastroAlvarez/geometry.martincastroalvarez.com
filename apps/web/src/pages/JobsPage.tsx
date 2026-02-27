import { Link } from "react-router-dom";
import { Container, Title, Text, Button, Badge } from "@geometry/ui";
import { useJobs } from "@geometry/data";

export const JobsPage = () => {
    const { data, isLoading } = useJobs();

    return (
        <Container padded spaced size={12}>
            <Container center>
                <Title xl center>
                    My Jobs
                </Title>
                <Text center>
                    {isLoading ? "Loading..." : `${data?.records.length ?? 0} job(s)`}
                </Text>
            </Container>
            {data?.records.map((job) => (
                <Container key={job.id} padded spaced size={12}>
                    <Link to={`/jobs/${job.id}`}>
                        <Button>
                            Job {job.id.slice(0, 8)}... <Badge danger={job.status === "failed"} success={job.status === "success"}>{job.status}</Badge>
                        </Button>
                    </Link>
                </Container>
            ))}
        </Container>
    );
};
