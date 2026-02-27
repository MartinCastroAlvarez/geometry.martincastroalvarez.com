/**
 * Top navigation bar: logo, title, and optional right-side children.
 *
 * Context: Two-column layout (logo+title left, children right); on mobile both columns full width.
 * Logo size is fixed (24px). Clicking the left block triggers optional onClick (e.g. go home).
 *
 * Example:
 *   <Nav onClick={() => navigate('/')}>
 *     <Button onClick={openMenu}>Menu</Button>
 *   </Nav>
 */

import { Container } from "./Container";
import { Logo } from "./Logo";
import { Title } from "./Title";
import { useDevice } from "./useDevice";

const LOGO_SIZE = 24;

interface NavProps {
    children?: React.ReactNode;
    onClick?: () => void;
}

export const Nav = ({ children, onClick }: NavProps) => {
    const { isMobile } = useDevice();

    return (
        <Container padded spaced middle rounded solid name="geometry-nav">
            <Container onClick={onClick} spaced size={isMobile ? 12 : 2} left>
                <div className="flex flex-row items-center gap-3">
                    <Logo size={LOGO_SIZE} />
                    <Title lg>Art Gallery</Title>
                </div>
            </Container>
            <Container middle spaced size={isMobile ? 12 : 10} right>
                {children}
            </Container>
        </Container>
    );
};
