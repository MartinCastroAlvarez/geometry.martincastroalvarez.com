/**
 * Single edge line between two vertices; hover/selected styling; optional click to add vertex on edge.
 *
 * Context: Renders a Konva Line from start to end. Stroke and width come from editorColors (selected > hover > default).
 * When onClick is provided, click/tap pass (x, y) of the pointer so the parent can insert a new vertex on the edge.
 *
 * Example:
 *   <Edge start={v1} end={v2} edgeIndex={i} selected onClick={handleEdgeClick} />
 */

import { memo, useState } from "react";
import { Line } from "react-konva";
import type { EditorVertex } from "./types";
import { editorColors } from "./colors";

export interface EdgeProps {
    start: EditorVertex;
    end: EditorVertex;
    edgeIndex: number;
    closed?: boolean;
    selected?: boolean;
    onClick?: (edgeIndex: number, x: number, y: number) => void;
}

const EdgeComponent = ({ start, end, edgeIndex, selected = false, onClick }: EdgeProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const stroke = selected
        ? editorColors.vertexActive
        : isHovered
          ? editorColors.strokeHover
          : editorColors.edge;
    const strokeWidth = selected ? 4 : isHovered ? 3 : 2;

    return (
        <Line
            points={[start.x, start.y, end.x, end.y]}
            stroke={stroke}
            strokeWidth={strokeWidth}
            hitStrokeWidth={20}
            lineCap="round"
            lineJoin="round"
            cursor="pointer"
            onClick={
                onClick
                    ? (e) => {
                          e.cancelBubble = true;
                          const pos = e.target.getStage()?.getPointerPosition?.();
                          if (pos) onClick(edgeIndex, pos.x, pos.y);
                      }
                    : undefined
            }
            onTap={
                onClick
                    ? (e) => {
                          e.cancelBubble = true;
                          const pos = e.target.getStage()?.getPointerPosition?.();
                          if (pos) onClick(edgeIndex, pos.x, pos.y);
                      }
                    : undefined
            }
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        />
    );
};

export const Edge = memo(EdgeComponent);
