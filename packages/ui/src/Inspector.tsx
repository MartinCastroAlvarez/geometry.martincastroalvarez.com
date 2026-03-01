/**
 * Read-only JSON inspector: displays arbitrary JSON inside a Container using react-json-view.
 *
 * Context: Used to inspect polygon data (boundary, obstacles) and other structured data.
 * Edit/add/delete are disabled; clipboard copy is enabled. Indent width 1.
 *
 * Example:
 *   <Inspector data={polygon.toDict()} />
 */

import React from "react";
import ReactJson from "react-json-view";
import { Theme, useTheme } from "@geometry/theme";
import { Scrollable } from "./Scrollable";

export interface InspectorProps {
    /** JSON-serializable data to display (object or array). */
    data: object;
    /** Max height of the JSON view container in pixels; overflow scrolls on the y-axis. Default 300. */
    size?: number;
}

/** react-json-view base16 theme: light theme (dark text) for light mode, dark theme (light text) for dark mode. */
const JSON_VIEW_THEME_LIGHT = "bright";
const JSON_VIEW_THEME_DARK = "monokai";

/** Data attribute for light-mode inspector; apps should add CSS so inner text uses theme color. */
export const INSPECTOR_LIGHT_ATTR = "data-inspector-light";

export const Inspector: React.FC<InspectorProps> = ({ data, size = 300 }) => {
    const { theme, getColor } = useTheme();
    const isLight = theme === Theme.Light;
    return (
        <Scrollable height={size} left>
            <div
                {...(isLight && {
                    [INSPECTOR_LIGHT_ATTR]: "",
                    style: {
                        color: getColor("--color-text"),
                        background: getColor("--color-bg")
                    }
                })}
            >
                <ReactJson
                    src={data}
                    name={false}
                    theme={isLight ? JSON_VIEW_THEME_LIGHT : JSON_VIEW_THEME_DARK}
                    indentWidth={2}
                    enableClipboard
                    displayDataTypes
                    collapsed={false}
                    collapseStringsAfterLength={50}
                    style={{
                        margin: 0,
                        padding: 10,
                        fontSize: "10px"
                    }}
                />
            </div>
        </Scrollable>
    );
};
