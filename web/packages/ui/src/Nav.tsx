// import React from "react";
import { Container } from "./Container";
import { Title } from "./Title";

// Simplified Nav for Geometry App
export function Nav() {
    const handleRefresh = () => {
        window.location.reload();
    };

    return (
        <Container padded>
            <Container spaced top>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    {/* Logo Section */}
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

                    {/* Right Side Actions (Placeholder for now) */}
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        {/* Add actions here if needed */}
                    </div>
                </div>
            </Container>
        </Container>
    );
};
