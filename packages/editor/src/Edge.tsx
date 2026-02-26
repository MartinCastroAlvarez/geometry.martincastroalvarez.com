import { Line } from "react-konva";
import type { EditorVertex } from "./models";

export interface EdgeProps {
    start: EditorVertex;
    end: EditorVertex;
    closed?: boolean;
    dashed?: boolean;
}

export function Edge({ start, end, closed = false, dashed = false }: EdgeProps) {
    return (
        <Line
            points={[start.x, start.y, end.x, end.y]}
            stroke={closed ? "#22c55e" : "#64748b"}
            strokeWidth={closed ? 2.5 : 2}
            lineCap="round"
            lineJoin="round"
            dash={dashed ? [8, 4] : undefined}
        />
    );
}
