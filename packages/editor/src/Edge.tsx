/**
 * Single edge line between two vertices; hover/selected styling; optional click to add vertex on edge.
 *
 * Context: Renders a Konva Line from start to end. Stroke and width come from editorColors (selected > hover > default).
 * When onClick is provided, click/tap pass (x, y) of the pointer so the parent can insert a new vertex on the edge.
 *
 * Example:
 *   <Edge start={v1} end={v2} selected onClick={(x, y) => handleEdgeClick(edgeIndex, x, y)} />
 */

import { Line } from "react-konva";
import type { EditorVertex } from "./types";
import { editorColors } from "./colors";

import { useState } from "react";

export interface EdgeProps {
    start: EditorVertex;
    end: EditorVertex;
    closed?: boolean;
    selected?: boolean;
    onClick?: (x: number, y: number) => void;
    readonly?: boolean;
}

export const Edge = ({ start, end, selected = false, onClick, readonly = false }: EdgeProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const stroke = selected
        ? editorColors.vertexActive
        : isHovered && !readonly
          ? editorColors.strokeHover
          : editorColors.edge;
    const strokeWidth = selected ? 4 : isHovered && !readonly ? 3 : 2;

    return (
        <Line
            points={[start.x, start.y, end.x, end.y]}
            stroke={stroke}
            strokeWidth={strokeWidth}
            hitStrokeWidth={20}
            lineCap="round"
            lineJoin="round"
            cursor={!readonly ? "pointer" : undefined}
            onClick={
                onClick
                    ? (e) => {
                          const pos = e.target.getStage()?.getPointerPosition?.();
                          if (pos) onClick(pos.x, pos.y);
                      }
                    : undefined
            }
            onTap={
                onClick
                    ? (e) => {
                          const pos = e.target.getStage()?.getPointerPosition?.();
                          if (pos) onClick(pos.x, pos.y);
                      }
                    : undefined
            }
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        />
    );
};
