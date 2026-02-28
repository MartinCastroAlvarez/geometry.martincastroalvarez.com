/**
 * Skeleton for the top Nav: Logo (real), title and right-side item skeletons.
 * Lives in apps/web/skeletons so the app controls nav loading state; uses @geometry/ui primitives.
 */
import {
    Skeleton,
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
        <Skeleton padded spaced middle rounded name="geometry-nav">
            <Skeleton size={isMobile ? 12 : 2} left>
                <div className="flex flex-row items-center gap-3">
                    <Logo size={LOGO_SIZE} />
                    <TitleSkeleton lg width="6rem" />
                </div>
            </Skeleton>
            <Skeleton middle spaced size={isMobile ? 12 : 10} right>
                <div className="flex w-full flex-row items-center gap-2 flex-wrap justify-end">
                    <ButtonSkeleton sm width={72} height={28} />
                    <TextSkeleton sm width="2.5rem" />
                    <ImageSkeleton size={20} rounded />
                    <TextSkeleton sm width="2rem" />
                    <ImageSkeleton size={28} rounded />
                    <TextSkeleton sm width="4rem" />
                    <TextSkeleton sm width="3rem" />
                </div>
            </Skeleton>
        </Skeleton>
    );
};
