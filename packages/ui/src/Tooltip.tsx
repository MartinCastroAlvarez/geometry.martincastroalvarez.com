/**
 * Generic tooltip using MUI: shows content on hover/focus/tap.
 * Styled with Tailwind to match the app (slate palette, rounded, typography).
 *
 * Example:
 *   <Tooltip title="Full text when truncated">
 *     <span className="truncate">Short text</span>
 *   </Tooltip>
 */

import React from "react";
import MuiTooltip, { TooltipProps as MuiTooltipProps } from "@mui/material/Tooltip";

const TOOLTIP_CLASSES =
    "geometry-tooltip !bg-slate-200 dark:!bg-slate-700 !text-slate-800 dark:!text-slate-100 !text-xs !font-medium !px-2.5 !py-1.5 !rounded-lg !shadow-md !border-0 !max-w-[min(90vw,20rem)]";

export interface TooltipProps extends Omit<MuiTooltipProps, "title"> {
    /** Content shown in the tooltip. */
    title: React.ReactNode;
    children: React.ReactElement;
}

export const Tooltip: React.FC<TooltipProps> = ({ title, children, slotProps, ...rest }) => {
    const tooltipSlot = slotProps?.tooltip as { className?: string } | undefined;
    const tooltipClassName = [TOOLTIP_CLASSES, tooltipSlot?.className].filter(Boolean).join(" ");
    return (
        <MuiTooltip
            title={title}
            slotProps={{
                ...slotProps,
                tooltip: { ...slotProps?.tooltip, className: tooltipClassName } as MuiTooltipProps["slotProps"] extends
                    { tooltip?: infer T }
                    ? T
                    : never,
            }}
            {...rest}
        >
            {children}
        </MuiTooltip>
    );
};
