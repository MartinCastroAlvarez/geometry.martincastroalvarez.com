/**
 * Generic tooltip using MUI: shows content on hover/focus/tap.
 * Use for accessible, styled tooltips (e.g. truncated text, icon hints).
 *
 * Example:
 *   <Tooltip title="Full text when truncated">
 *     <span className="truncate">Short text</span>
 *   </Tooltip>
 */

import React from "react";
import MuiTooltip, { TooltipProps as MuiTooltipProps } from "@mui/material/Tooltip";

export interface TooltipProps extends Omit<MuiTooltipProps, "title"> {
    /** Content shown in the tooltip. */
    title: React.ReactNode;
    children: React.ReactElement;
}

export const Tooltip: React.FC<TooltipProps> = ({ title, children, ...rest }) => {
    return (
        <MuiTooltip title={title} {...rest}>
            {children}
        </MuiTooltip>
    );
};
