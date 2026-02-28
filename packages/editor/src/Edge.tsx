/**
 * Single edge line between two vertices; same color as Vertex (Tailwind --color-primary), no border.
 *
 * Context: Konva Line; stroke from editorColors.color (Tailwind theme). When onClick is provided,
 * click/tap pass (x, y) so the parent can insert a new vertex on the edge.
 *
 * Example:
 *   <Edge start={v1} end={v2} edgeIndex={i} onClick={handleEdgeClick} />
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
    /** Canvas scale (zoom); used to keep visual stroke width constant. Default 1. */
    scale?: number;
}

const EdgeComponent = ({ start, end, edgeIndex, selected = false, onClick, scale = 1 }: EdgeProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const baseStrokeWidth = selected ? 4 : isHovered ? 3 : 2;
    const strokeWidth = baseStrokeWidth / scale;

    return (
        <Line
            points={[start.x, start.y, end.x, end.y]}
            stroke={editorColors.color}
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
