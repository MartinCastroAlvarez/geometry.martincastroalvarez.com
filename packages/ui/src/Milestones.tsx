/**
 * Milestones: horizontal step indicator. Only accepts Milestone children.
 * Renders circles (completed = checkmark, current = number with border, future = faded number)
 * with connecting lines. Reuses existing Tailwind theme (primary, slate).
 */

import React, { isValidElement, Children, cloneElement } from "react";

export type MilestoneStepStatus = "completed" | "current" | "future";

export interface MilestoneProps {
    completed: boolean;
    children: React.ReactNode;
    /** Injected by Milestones; do not pass manually. */
    stepIndex?: number;
    /** Injected by Milestones; do not pass manually. */
    stepStatus?: MilestoneStepStatus;
}

const MilestoneComponent: React.FC<MilestoneProps> = ({
    completed,
    children,
    stepIndex = 1,
    stepStatus = completed ? "completed" : "current",
}) => {
    const status = stepStatus;
    const isCompleted = status === "completed";
    const isCurrent = status === "current";
    const isFuture = status === "future";

    const circleClasses =
        "shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium border-2";
    const circleVariant =
        isCompleted
            ? "bg-primary-400 border-primary-400 text-white"
            : isCurrent
              ? "bg-none border-primary-400 text-slate-600 dark:text-slate-400"
              : "bg-none border-slate-400 dark:border-slate-600 text-slate-500";

    const labelClasses =
        "text-xs font-medium mt-2 text-center " +
        (isFuture ? "text-slate-500" : "text-slate-700 dark:text-slate-300");

    return (
        <div className="geometry-milestone flex flex-col items-center min-w-0 flex-1">
            <div className={`${circleClasses} ${circleVariant}`}>
                {isCompleted ? (
                    <span aria-hidden>✓</span>
                ) : (
                    <span aria-hidden>{stepIndex}</span>
                )}
            </div>
            <span className={labelClasses}>{children}</span>
        </div>
    );
};

MilestoneComponent.displayName = "Milestone";

export const Milestone = MilestoneComponent;

export interface MilestonesProps {
    children: React.ReactNode;
}

export const Milestones: React.FC<MilestonesProps> = ({ children }) => {
    const items = Children.toArray(children).filter(
        (child): child is React.ReactElement<MilestoneProps> =>
            isValidElement(child) &&
            (child.type === Milestone ||
                (child.type as React.ComponentType & { displayName?: string })?.displayName === "Milestone")
    );

    let firstIncompleteIndex = -1;
    items.forEach((el, i) => {
        if (firstIncompleteIndex === -1 && !el.props.completed) firstIncompleteIndex = i;
    });

    const rendered = items.map((child, index) => {
        const completed = child.props.completed;
        const stepStatus: MilestoneStepStatus =
            completed ? "completed" : index === firstIncompleteIndex ? "current" : "future";
        const showConnector = index < items.length - 1;
        const connectorCompleted = completed;

        return (
            <React.Fragment key={index}>
                {cloneElement(child, {
                    stepIndex: index + 1,
                    stepStatus,
                })}
                {showConnector && (
                    <div
                        className="shrink-0 flex-1 min-w-4 h-1 mx-0.5 rounded mt-[0.875rem]"
                        aria-hidden
                    >
                        <div
                            className={`w-full h-full rounded ${
                                connectorCompleted ? "bg-primary-400" : "bg-slate-300 dark:bg-slate-600"
                            }`}
                        />
                    </div>
                )}
            </React.Fragment>
        );
    });

    return (
        <div
            className="geometry-milestones flex flex-row items-start w-full p-4 gap-0"
            role="list"
            aria-label="Progress"
        >
            {rendered}
        </div>
    );
};

Milestones.displayName = "Milestones";
