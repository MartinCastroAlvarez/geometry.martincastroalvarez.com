/**
 * Skeleton for the top Nav: matches Nav layout (logo + title left, toolbar right).
 * Uses Skeleton as full-width container; inner content mirrors App.tsx (Create, History, toggles, user, Login/Logout).
 */
import {
    Skeleton,
    Container,
    Logo,
    useDevice,
    ButtonSkeleton,
    TextSkeleton,
    TitleSkeleton,
    ImageSkeleton,
} from "@geometry/ui";

const LOGO_SIZE = 24;

export const NavSkeleton = () => {
    const { isMobile } = useDevice();

    return (
        <Skeleton>
            <Container padded spaced middle rounded name="geometry-nav">
                <Container spaced size={isMobile ? 12 : 2} left>
                    <div className="flex flex-row items-center gap-3">
                        <Logo size={LOGO_SIZE} />
                        <TitleSkeleton lg width="6rem" />
                    </div>
                </Container>
                <Container middle spaced size={isMobile ? 12 : 10} right>
                    <div className="flex w-full flex-row items-center gap-2 flex-wrap justify-end">
                        <ButtonSkeleton sm width={72} height={28} />
                        <ButtonSkeleton sm width={64} height={28} />
                        <div className="flex items-center gap-1.5">
                            <ImageSkeleton size={20} rounded />
                            <TextSkeleton sm width="2rem" />
                        </div>
                        <div className="flex items-center gap-1.5">
                            <ImageSkeleton size={20} rounded />
                            <TextSkeleton sm width="3rem" />
                        </div>
                        <ImageSkeleton size={28} rounded />
                        <ButtonSkeleton sm width={56} height={28} />
                    </div>
                </Container>
            </Container>
        </Skeleton>
    );
};
