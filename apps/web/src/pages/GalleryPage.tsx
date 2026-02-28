/**
 * Public gallery view by ID.
 *
 * Context: This page displays a single published art gallery by its ID from the URL (route param :id).
 * It is intended for public, shareable links—no authentication is required. useArtGallery(id) fetches
 * the gallery from the API; the response includes title and id, which are shown centered at the top.
 *
 * If the ID is missing (e.g. navigation to /gallery without an id), the page shows a short message
 * that the gallery ID is required. While the gallery is loading or missing, GalleryPageSkeleton wraps
 * the content so the layout remains consistent. Analytics: GALLERY_VIEW is tracked when the gallery
 * has loaded successfully, with the gallery id as the label.
 */
import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { Container, Title, Text } from "@geometry/ui";
import { useArtGallery } from "@geometry/data";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { WithGalleryPageSkeleton } from "../skeletons";

export const GalleryPage = () => {
    const { id } = useParams<{ id: string }>();
    const { gallery, isLoading } = useArtGallery(id ?? null);
    const { track } = useAnalytics();
    const loading = isLoading || !gallery;

    useEffect(() => {
        if (id && !isLoading && gallery) {
            track({
                action: GoogleAnalyticsActions.GALLERY_VIEW,
                category: GoogleAnalyticsCategories.PAGE,
                label: id,
            });
        }
    }, [id, isLoading, gallery, track]);

    if (!id) return <Container padded spaced><Text>Gallery ID required</Text></Container>;

    return (
        <WithGalleryPageSkeleton loading={loading}>
            <Container padded spaced>
            <Container center>
                <Title xl center>
                    {gallery!.title ?? "Untitled Art Gallery"}
                </Title>
                <Text center>ID: {gallery!.id}</Text>
            </Container>
            </Container>
        </WithGalleryPageSkeleton>
    );
};
