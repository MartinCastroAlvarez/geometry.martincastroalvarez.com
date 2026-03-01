/**
 * Home page (landing).
 *
 * Context: This is the root landing page, rendered at /. It currently renders a minimal layout
 * (a padded, spaced container with no inner content) so the app has a stable entry point. The page
 * uses useSession so that the loading state is consistent across the app: while the session is
 * resolving, HomePageSkeleton is shown, avoiding layout jumps or partial content. Once loaded,
 * the user can navigate to the editor, jobs list, or other routes. The page is intentionally
 * minimal and can be extended later with marketing copy, featured galleries, or a dashboard.
 */
import { useSession } from "@geometry/data";
import { Page } from "@geometry/ui";
import { HomePageSkeleton } from "../skeletons";

export const HomePage = () => {
    const { isLoading: sessionLoading } = useSession();

    if (sessionLoading) return <HomePageSkeleton />;

    return <Page />;
};
