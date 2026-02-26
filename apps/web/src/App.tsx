import { useCallback } from "react";
import { Editor } from "@geometry/editor";
import { Toaster, Nav, Container, Title, Text, Body } from "@geometry/ui";
import { useSession, useLogout } from "@geometry/data";
import { useEditor } from "./store";
import "./index.css";

function App() {
    const { data: user } = useSession();
    const logout = useLogout();
    const { gallery, setPerimeter, setHoles } = useEditor((s) => s);

    const handleChange = useCallback(
        (boundary?: import("@geometry/domain").Polygon, obstacles?: import("@geometry/domain").Polygon[]) => {
            if (boundary) setPerimeter(boundary);
            if (obstacles) setHoles(obstacles);
        },
        [setPerimeter, setHoles]
    );

    return (
        <Body>
            <Toaster />
            <Nav
                {...(user && {
                    userName: user.name ?? undefined,
                    userImageUrl: user.avatarUrl ?? undefined,
                    onLogout: logout,
                })}
                onLogin={logout}
            />
            <Container padded size={12}>
                <Container size={8} center>
                    <Container center>
                        <Title xl center>
                            🎨 Geometry Art Gallery Editor
                        </Title>
                        <Text center size={600}>
                            Editor visual interactivo para el Art Gallery Problem
                        </Text>
                    </Container>

                    <Editor
                        boundary={gallery.perimeter}
                        obstacles={gallery.holes}
                        width={850}
                        height={550}
                        onChange={handleChange}
                        readonly={false}
                    />
                </Container>
            </Container>
        </Body>
    );
}

export default App;
