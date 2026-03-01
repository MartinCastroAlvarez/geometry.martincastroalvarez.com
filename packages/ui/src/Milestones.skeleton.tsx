/**
 * Skeleton for Milestones. Matches Milestones layout: horizontal row of step circles with
 * connectors and labels. Renders 5 placeholder items (circle + label bar) for loading states.
 *
 * Example:
 *   {childrenLoading ? <MilestonesSkeleton /> : <Milestones>...</Milestones>}
 */

import React from "react";

const MILESTONE_COUNT = 5;

export const MilestonesSkeleton: React.FC = () => {
    return (
        <div
            className="geometry-milestones flex flex-row items-start w-full p-4 gap-0"
            role="presentation"
            aria-hidden
        >
            {Array.from({ length: MILESTONE_COUNT }, (_, index) => (
                <React.Fragment key={index}>
                    <div className="geometry-milestone flex flex-col items-center min-w-0 flex-1">
                        <div
                            className="shrink-0 w-8 h-8 rounded-full bg-slate-700 animate-pulse"
                            aria-hidden
                        />
                        <div
                            className="mt-2 h-3 w-12 rounded bg-slate-700 animate-pulse mx-auto"
                            aria-hidden
                        />
                    </div>
                    {index < MILESTONE_COUNT - 1 && (
                        <div
                            className="shrink-0 flex-1 min-w-4 h-1 mx-0.5 rounded mt-[0.875rem] bg-slate-700 animate-pulse"
                            aria-hidden
                        />
                    )}
                </React.Fragment>
            ))}
        </div>
    );
};

MilestonesSkeleton.displayName = "MilestonesSkeleton";
