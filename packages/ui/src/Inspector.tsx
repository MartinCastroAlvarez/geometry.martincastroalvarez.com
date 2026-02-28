/**
 * Read-only JSON inspector: displays arbitrary JSON inside a Container using @uiw/react-json-view.
 *
 * Context: Used to inspect polygon data (boundary, obstacles) and other structured data. Styling
 * uses theme variables via useTheme().getColor/getVar so colors come from theme.css; no custom
 * colors or className are defined. Not editable; for inspection only.
 *
 * Example:
 *   <Inspector data={polygon.toDict()} />
 */

import React from "react";
import JsonView from "@uiw/react-json-view";
import { useTheme } from "@geometry/theme";
import { Container } from "./Container";

export interface InspectorProps {
    /** JSON-serializable data to display (object or array). */
    data: object;
}

export const Inspector: React.FC<InspectorProps> = ({ data }) => {
    const { getColor } = useTheme();
    const themeStyle: React.CSSProperties = {
        ["--w-rjv-color" as string]: getColor("--color-text"),
        ["--w-rjv-background-color" as string]: getColor("--color-bg"),
        ["--w-rjv-line-color" as string]: getColor("--color-slate-700"),
        ["--w-rjv-arrow-color" as string]: getColor("--color-text"),
        ["--w-rjv-edit-key" as string]: getColor("--color-text"),
        ["--w-rjv-info-color" as string]: getColor("--color-text"),
        ["--w-rjv-type-string-color" as string]: getColor("--color-success-400"),
        ["--w-rjv-type-int-color" as string]: getColor("--color-primary-400"),
        ["--w-rjv-type-float-color" as string]: getColor("--color-primary-400"),
        ["--w-rjv-type-boolean-color" as string]: getColor("--color-primary-400"),
        ["--w-rjv-type-null-color" as string]: getColor("--color-slate-400"),
    };
    return (
        <Container padded rounded>
            <JsonView value={data} style={themeStyle} />
        </Container>
    );
};
