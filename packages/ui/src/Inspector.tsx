/**
 * Read-only JSON inspector: displays arbitrary JSON inside a Container as formatted plain text.
 *
 * Context: Used to inspect polygon data (boundary, obstacles) and other structured data. Styling
 * uses Tailwind theme colors (slate). Not editable; for inspection only. JSON is always fully
 * visible (non-collapsible).
 *
 * Example:
 *   <Inspector data={polygon.toDict()} />
 */

import React from "react";
import { Container } from "./Container";

export interface InspectorProps {
    /** JSON-serializable data to display (object or array). */
    data: object;
    /** Height of the JSON view container in pixels; overflow scrolls on the y-axis. Default 300. */
    size?: number;
}

export const Inspector: React.FC<InspectorProps> = ({ data, size = 300 }) => {
    const jsonString = JSON.stringify(data, null, 2).replace(/^\s+/gm, "");
    return (
        <Container height={size}>
            <pre className="m-0 text-xs font-mono text-slate-200 bg-slate-900 overflow-auto whitespace-pre-wrap break-words">
                {jsonString}
            </pre>
        </Container>
    );
};
