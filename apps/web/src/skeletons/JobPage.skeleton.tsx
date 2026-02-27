/**
 * Skeleton for single Job page. Reuses @geometry/ui skeletons.
 */
import { Container, TitleSkeleton, BadgeSkeleton, InputSkeleton, ButtonSkeleton } from "@geometry/ui";

export const JobPageSkeleton = () => (
    <Container padded spaced size={12}>
        <Container center>
            <TitleSkeleton xl width="10rem" />
            <BadgeSkeleton width="4rem" />
        </Container>
        <Container padded spaced size={12}>
            <InputSkeleton width="100%" />
        </Container>
        <Container padded spaced size={12}>
            <div className="flex gap-2">
                <ButtonSkeleton width={90} height={32} />
                <ButtonSkeleton width={100} height={32} />
            </div>
        </Container>
        <Container padded spaced size={12}>
            <ButtonSkeleton width={120} height={32} />
        </Container>
    </Container>
);
