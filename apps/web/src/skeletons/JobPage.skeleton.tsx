/**
 * Skeleton for single Job page. Reuses @geometry/ui skeletons.
 * WithJobPageSkeleton shows skeleton when loading, otherwise renders children.
 */
import type { ReactNode } from "react";
import { Skeleton, TitleSkeleton, BadgeSkeleton, InputSkeleton, ButtonSkeleton } from "@geometry/ui";

export const JobPageSkeleton = () => (
    <Skeleton padded spaced>
        <Skeleton center>
            <TitleSkeleton xl width="10rem" />
            <BadgeSkeleton width="4rem" />
        </Skeleton>
        <Skeleton padded spaced>
            <InputSkeleton width="100%" />
        </Skeleton>
        <Skeleton padded spaced>
            <div className="flex gap-2">
                <ButtonSkeleton width={90} height={32} />
                <ButtonSkeleton width={100} height={32} />
            </div>
        </Skeleton>
        <Skeleton padded spaced>
            <ButtonSkeleton width={120} height={32} />
        </Skeleton>
    </Skeleton>
);

export function WithJobPageSkeleton({ loading, children }: { loading: boolean; children: ReactNode }) {
    return loading ? <JobPageSkeleton /> : <>{children}</>;
}
