/**
 * Skeleton for the top Nav: Logo (always real), title skeleton left; right-side item skeletons.
 *
 * Context: Matches Nav layout and App.tsx nav contents. Logo is always the real Logo component
 * (not a skeleton). Right side skeletons: Create button, Jobs link, language selector (globe + EN),
 * user block (name + avatar), Login/Logout link. Uses ButtonSkeleton, TextSkeleton, TitleSkeleton,
 * ImageSkeleton. No external skeleton library (same approach as time app).
 */

import { Container } from "./Container";
import { Logo } from "./Logo";
import { useDevice } from "./useDevice";
import { ButtonSkeleton } from "./Button.skeleton";
import { TextSkeleton } from "./Text.skeleton";
import { TitleSkeleton } from "./Title.skeleton";
import { ImageSkeleton } from "./Image.skeleton";

const LOGO_SIZE = 24;

export const NavSkeleton = () => {
    const { isMobile } = useDevice();

    return (
        <Container padded spaced middle rounded solid name="geometry-nav">
            <Container size={isMobile ? 12 : 2} left>
                <div className="flex flex-row items-center gap-3">
                    <Logo size={LOGO_SIZE} />
                    <TitleSkeleton lg width="6rem" />
                </div>
            </Container>
            <Container middle spaced size={isMobile ? 12 : 10} right>
                <div className="flex flex-row items-center gap-2 flex-wrap justify-end">
                    <ButtonSkeleton sm width={72} height={28} />
                    <TextSkeleton sm width="2.5rem" />
                    <ImageSkeleton size={20} rounded />
                    <TextSkeleton sm width="2rem" />
                    <ImageSkeleton size={28} rounded />
                    <TextSkeleton sm width="4rem" />
                    <TextSkeleton sm width="3rem" />
                </div>
            </Container>
        </Container>
    );
};
