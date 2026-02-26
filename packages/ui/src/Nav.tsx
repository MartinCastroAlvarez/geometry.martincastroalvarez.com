import { Container } from "./Container";
import { Image } from "./Image";
import { Button } from "./Button";
import { Text } from "./Text";
import { useDevice } from "./useDevice";

const SRC = "https://media.martincastroalvarez.com/icon/geometry/favicon.ico";
const SIZE = 32;

interface NavProps {
    userName?: string;
    userImageUrl?: string;
    onLogout?: () => void;
    onLogin?: () => void;
}

export function Nav({ userName, userImageUrl, onLogout, onLogin }: NavProps) {
    const { isMobile } = useDevice();
    const handleRefresh = () => window.location.reload();
    const colSize = isMobile ? 12 : 6;

    return (
        <Container padded spaced middle name="geometry-nav">
            <Container onClick={handleRefresh} middle spaced size={colSize} left>
                <Image src={SRC} size={SIZE} rounded />
            </Container>
            <Container middle spaced size={colSize} right>
                <Text>{userName}</Text>
                <Image src={userImageUrl} size={SIZE} rounded />
                {Boolean(userName) && onLogout != null && (
                    <Button onClick={onLogout} sm>
                        Logout
                    </Button>
                )}
                {!Boolean(userName) && onLogin != null && (
                    <Button onClick={onLogin} sm>
                        Login
                    </Button>
                )}
            </Container>
        </Container>
    );
}
