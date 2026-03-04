/**
 * Public gallery view by ID.
 *
 * Context: Displays a single published art gallery by URL param :id. useArtGallery(id) from
 * @geometry/data fetches the gallery. Viewer (non-interactive); below: 2 cols (desktop/tablet),
 * 1 on mobile—left: title (no badges), muted "Updated" + humanized timestamp; right: Edit button
 * that navigates to /design with same shape and "Copy of" + title. GalleryPageSkeleton while loading.
 */
import { useCallback, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import { enUS, es } from "date-fns/locale";
import { Page, Container, Title, Text, Toolbar, Button, useDevice } from "@geometry/ui";
import { Viewer, Summary } from "@geometry/editor";
import { useArtGallery } from "@geometry/data";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { Language, useLocale } from "@geometry/i18n";
import { Pencil } from "lucide-react";
import { GalleryPageSkeleton } from "../skeletons";

const VIEWER_HEIGHT = 520;

export const GalleryPage = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { t, language } = useLocale();
    const { isMobile } = useDevice();
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

    const handleEditClick = useCallback(() => {
        if (!gallery) return;
        const copyOfPrefix = t("editor.copyOf");
        const rawTitle = typeof gallery.title === "string" && gallery.title.trim() ? gallery.title : t("editor.untitledGallery");
        const trimmed = rawTitle.trimStart();
        const alreadyCopyOf =
            copyOfPrefix.length > 0 &&
            trimmed.toLowerCase().startsWith(copyOfPrefix.trim().toLowerCase());
        const titleForEditor = alreadyCopyOf ? rawTitle : copyOfPrefix + trimmed;
        navigate("/design", {
            state: { artGallery: gallery.artGallery, title: titleForEditor },
        });
    }, [navigate, gallery, t]);

    if (!id) {
        return (
            <Page>
                <Container padded spaced>
                    <Text>Gallery ID required</Text>
                </Container>
            </Page>
        );
    }

    if (loading) return <GalleryPageSkeleton />;

    const dateFnsLocale = language === Language.ES ? es : enUS;
    const updatedLabel =
        gallery!.updated_at && !Number.isNaN(Date.parse(gallery!.updated_at))
            ? `${t("gallery.updated")} ${formatDistanceToNow(new Date(gallery!.updated_at), { addSuffix: true, locale: dateFnsLocale })}`
            : t("gallery.updated");

    const title =
        typeof gallery!.title === "string" && gallery!.title.trim()
            ? gallery!.title
            : t("editor.untitledGallery");

    return (
        <Page>
            <Container padded spaced>
                <Container size={12} left center>
                    <Summary artGallery={gallery!.artGallery} />
                </Container>
            </Container>
            <Container padded spaced>
                <Viewer artGallery={gallery!.artGallery} size={VIEWER_HEIGHT} vertices />
            </Container>
            <Container padded spaced>
                <Container size={isMobile ? 12 : 6} left={!isMobile} center={isMobile}>
                    <Container size={12} left={!isMobile} center={isMobile}>
                        <Title xl left={!isMobile} center={isMobile}>
                            {title}
                        </Title>
                    </Container>
                    <Container size={12} left={!isMobile} center={isMobile}>
                        <Text muted xxs left={!isMobile} center={isMobile}>
                            {updatedLabel}
                        </Text>
                    </Container>
                </Container>
                <Container size={isMobile ? 12 : 6} center={isMobile} right={!isMobile}>
                    <Toolbar right={!isMobile} center={isMobile}>
                        <Button
                            onClick={handleEditClick}
                            icon={<Pencil size={16} aria-hidden />}
                            primary
                            sm
                            aria-label={t("gallery.edit")}
                        >
                            {t("gallery.edit")}
                        </Button>
                    </Toolbar>
                </Container>
            </Container>
        </Page>
    );
};
