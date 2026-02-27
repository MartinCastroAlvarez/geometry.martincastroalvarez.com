/**
 * Home page (landing).
 *
 * Context: Rendered at /. Shows HomePageSkeleton while useSession is loading so
 * the app shows a consistent loading state. Can be extended for marketing or galleries list.
 */
import { useSession } from "@geometry/data";
import { Container } from "@geometry/ui";
import { WithHomePageSkeleton } from "../skeletons";

export const HomePage = () => {
    const { isLoading: sessionLoading } = useSession();

    return (
        <WithHomePageSkeleton loading={sessionLoading}>
            <Container padded spaced size={12} />
        </WithHomePageSkeleton>
    );
};
