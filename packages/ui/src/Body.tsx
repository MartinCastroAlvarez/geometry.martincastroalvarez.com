/**
 * Page body layout: responsive side/middle columns and full-height shell.
 *
 * Context: Uses useDevice to choose layout; on mobile/tablet middle is full width (12), sides 0.
 * On desktop, middle is 8 cols with 2-col sides. The last child (main content) is in a
 * scrollable region so the page can scroll when content overflows; nav and toaster stay fixed.
 *
 * Example:
 *   <Body>
 *     <Title>Page</Title>
 *     <Text>Content here.</Text>
 *   </Body>
 */

import React from "react";
import { useDevice } from "./useDevice";

interface BodyProps {
    children?: React.ReactNode;
}

export const Body: React.FC<BodyProps> = ({ children }) => {
    const { isMobile, isTablet } = useDevice();
    const hideSides = isMobile || isTablet;
    const childrenArray = React.Children.toArray(children);

    return (
        <div
            className="geometry-body flex flex-col flex-1 min-h-0 overflow-hidden font-sans text-slate-800 dark:text-slate-100"
            style={{ background: "var(--body-gradient)" }}
        >
            <div className="flex-1 min-h-0 overflow-hidden grid grid-cols-12 w-full">
                {!hideSides && <div className="col-span-2" />}
                <div
                    className={`flex flex-col min-h-0 ${hideSides ? "col-span-12" : "col-span-8"}`}
                >
                    {childrenArray.map((child, index) => {
                        const isLast = index === childrenArray.length - 1;
                        return (
                            <div
                                key={index}
                                className={
                                    isLast
                                        ? "flex-1 min-h-0 overflow-y-auto"
                                        : "flex-shrink-0"
                                }
                            >
                                {child}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};
