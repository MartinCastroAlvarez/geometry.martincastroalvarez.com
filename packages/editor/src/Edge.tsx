/**
 * Single edge line between two vertices; same color as Vertex (theme --color-polygon), no border.
 *
 * Context: Konva Line; stroke from useTheme().getColor (theme.css). When stitched is true,
 * the edge uses --color-edge-stitched (theme-specific: subtle in dark, lighter in light).
 *
 * Example:
 *   <Edge start={v1} end={v2} edgeIndex={i} onClick={handleEdgeClick} />
 *   <Edge start={v1} end={v2} edgeIndex={i} stitched scale={scale} />
 */

import { memo, useState } from "react";
import { Line } from "react-konva";
import { useTheme } from "@geometry/theme";
import type { EditorVertex } from "./types";

export interface EdgeProps {
    start: EditorVertex;
    end: EditorVertex;
    edgeIndex: number;
    closed?: boolean;
    selected?: boolean;
    /** When true, edge is drawn dimmer and thinner (stitched polygon edges not on boundary/obstacles). */
    stitched?: boolean;
    onClick?: (edgeIndex: number, x: number, y: number) => void;
    /** Canvas scale (zoom); used to keep visual stroke width constant. Default 1. */
    scale?: number;
}

const EdgeComponent = ({ start, end, edgeIndex, selected = false, stitched = false, onClick, scale = 1 }: EdgeProps) => {
    const { getColor } = useTheme();
    const [isHovered, setIsHovered] = useState(false);
    const baseStrokeWidth = stitched ? 1 : selected ? 4 : isHovered ? 3 : 2;
    const strokeWidth = baseStrokeWidth / scale;
    const stroke = stitched ? getColor("--color-edge-stitched") : getColor("--color-polygon");

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
