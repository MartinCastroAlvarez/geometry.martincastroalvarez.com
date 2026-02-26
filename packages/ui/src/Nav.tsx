import { Container } from "./Container";
import { Image } from "./Image";
import { useDevice } from "./useDevice";

const SRC = "https://media.martincastroalvarez.com/icon/geometry/favicon.ico";
const SIZE = 32;

interface NavProps {
    children?: React.ReactNode;
    onClick?: () => void;
}

export const Nav = ({ children, onClick }: NavProps) => {
    const { isMobile } = useDevice();
    const colSize = isMobile ? 12 : 6;

    return (
        <Container padded spaced middle name="geometry-nav">
            <Container onClick={onClick} middle spaced size={colSize} left>
                <Image src={SRC} size={SIZE} rounded />
            </Container>
            <Container middle spaced size={colSize} right>
                {children}
            </Container>
        </Container>
    );
};
