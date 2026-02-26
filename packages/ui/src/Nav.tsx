import { Container } from "./Container";
import { Title } from "./Title";

export function Nav() {
    const handleRefresh = () => window.location.reload();

    return (
        <Container padded>
            <Container spaced top>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <div onClick={handleRefresh} style={{ cursor: 'pointer' }}>
                        <Container center middle horizontal spaced>
                            <img
                                src="https://media.martincastroalvarez.com/icon/geometry/favicon.ico"
                                alt="Geometry Logo"
                                style={{ width: '28px', height: '28px', borderRadius: '50%' }}
                            />
                            <Title xl>Art Gallery</Title>
                        </Container>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }} />
                </div>
            </Container>
        </Container>
    );
}
