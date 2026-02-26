import { useParams } from "react-router-dom";
import { Container, Title, Text } from "@geometry/ui";
import { useArtGallery } from "@geometry/data";

export const GalleryPage = () => {
    const { id } = useParams<{ id: string }>();
    const { data: gallery, isLoading } = useArtGallery(id ?? null);

    if (!id) return <Text>Gallery ID required</Text>;
    if (isLoading || !gallery) return <Text>Loading...</Text>;

    return (
        <Container padded spaced size={12}>
            <Container center>
                <Title xl center>
                    {gallery.title ?? "Untitled Art Gallery"}
                </Title>
                <Text center>ID: {gallery.id}</Text>
            </Container>
        </Container>
    );
};
