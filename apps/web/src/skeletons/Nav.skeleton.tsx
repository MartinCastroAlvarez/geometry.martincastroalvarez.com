/**
 * Skeleton for the top Nav: matches Nav layout (logo + title left, toolbar right).
 * Uses Skeleton as full-width container; inner content mirrors App.tsx (Create, History, toggles, user, Login/Logout).
 * Wrapper has min-height and flex-shrink-0 so the bar is never squeezed by the Body flex layout.
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
/** Fixed height so the skeleton row never collapses in the Body grid; matches real nav (p-4 + content). */
const NAV_BAR_HEIGHT = "4rem";

export const NavSkeleton = () => {
    const { isMobile } = useDevice();

    return (
        <div
            className="w-full flex-shrink-0 flex flex-col justify-center"
            style={{ minHeight: NAV_BAR_HEIGHT, height: NAV_BAR_HEIGHT }}
        >
            <Skeleton fullHeight={false} className="h-full">
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
        </div>
    );
};
