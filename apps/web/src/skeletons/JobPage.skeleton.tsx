/**
 * Skeleton for single Job page. Reuses @geometry/ui skeletons.
 */
import { Skeleton, Container, TitleSkeleton, BadgeSkeleton, InputSkeleton, ButtonSkeleton } from "@geometry/ui";

export const JobPageSkeleton = () => (
    <Skeleton>
        <Container padded spaced>
            <Container center>
                <TitleSkeleton xl width="10rem" />
                <BadgeSkeleton width="4rem" />
            </Container>
            <Container padded spaced>
                <InputSkeleton width="100%" />
            </Container>
            <Container padded spaced>
                <div className="flex gap-2">
                    <ButtonSkeleton width={90} height={32} />
                    <ButtonSkeleton width={100} height={32} />
                </div>
            </Container>
            <Container padded spaced>
                <ButtonSkeleton width={120} height={32} />
            </Container>
        </Container>
    </Skeleton>
);
