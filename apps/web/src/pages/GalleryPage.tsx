/**
 * Public gallery view by ID.
 *
 * Context: useArtGallery(id) fetches published gallery; shows title and id. Route
 * /:id (after /jobs, /design) is public—no session required.
 */
import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { Container, Title, Text } from "@geometry/ui";
import { useArtGallery } from "@geometry/data";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";

export const GalleryPage = () => {
    const { id } = useParams<{ id: string }>();
    const { gallery, isLoading } = useArtGallery(id ?? null);
    const { track } = useAnalytics();

    useEffect(() => {
        if (id && !isLoading && gallery) {
            track({
                action: GoogleAnalyticsActions.GALLERY_VIEW,
                category: GoogleAnalyticsCategories.PAGE,
                label: id,
            });
        }
    }, [id, isLoading, gallery, track]);

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
