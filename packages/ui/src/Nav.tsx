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
    const colSize = isMobile ? 12 : 6;

    return (
        <Container padded spaced middle rounded solid name="geometry-nav">
            <Container onClick={onClick} spaced size={colSize} left>
                <div className="flex flex-row items-center gap-3">
                    <Logo size={LOGO_SIZE} />
                    <Title lg>Art Gallery</Title>
                </div>
            </Container>
            <Container middle spaced size={colSize} right>
                {children}
            </Container>
        </Container>
    );
};
