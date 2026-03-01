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
import { Scrollable } from "./Scrollable";

export interface InspectorProps {
    /** JSON-serializable data to display (object or array). */
    data: object;
    /** Max height of the JSON view container in pixels; overflow scrolls on the y-axis. Default 300. */
    size?: number;
}

export const Inspector: React.FC<InspectorProps> = ({ data, size = 300 }) => {
    return (
        <Scrollable maxHeight={size} left>
            <ReactJson
                src={data}
                name={false}
                theme="ashes"
                indentWidth={1}
                enableClipboard
                displayDataTypes
                collapsed={false}
                collapseStringsAfterLength={10}
                style={{
                    margin: 0,
                    background: "none",
                    padding: 10,
                    fontSize: "10px"
                }}
            />
        </Scrollable>
    );
};
