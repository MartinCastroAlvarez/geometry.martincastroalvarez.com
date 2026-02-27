/**
 * Draggable vertex circle with first/active/hover styling and optional drag/click handlers.
 *
 * Context: Renders a Konva Circle; radius and fill/stroke come from editorColors (isFirst, isActive, hover).
 * dragBoundFunc clamps position to dragBounds [0,0]–[width,height] when provided. onDragMove receives (x, y).
 *
 * Example:
 *   <Vertex vertex={v} isActive onDragMove={(x, y) => handleVertexDrag(i, x, y)} onClick={() => handleVertexClick(i)} />
 */

import { useState } from "react";
import { Circle } from "react-konva";
import type { EditorVertex } from "./types";
import { editorColors } from "./colors";

export interface VertexProps {
    vertex: EditorVertex;
    isFirst?: boolean;
    isActive?: boolean;
    onDragMove?: (x: number, y: number) => void;
    onDragEnd?: () => void;
    onClick?: () => void;
    draggable?: boolean;
    readonly?: boolean;
    /** Constrain drag within bounds [0,0] to [width,height] */
    dragBounds?: { width: number; height: number };
    /** When set, constrain drag to this rect instead of [0,0]–[dragBounds.width,dragBounds.height] */
    contentBounds?: { minX: number; minY: number; maxX: number; maxY: number };
}

export const Vertex = ({
    vertex,
    isFirst = false,
    isActive = false,
    onDragMove,
    onDragEnd,
    onClick,
    draggable = true,
    dragBounds,
    contentBounds,
    readonly = false,
}: VertexProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const radius = isActive ? 8 : isFirst ? 7 : isHovered ? 6 : 5;
    const strokeWidth = isHovered && !readonly ? 3 : 2;

    const dragBoundFunc =
        onDragMove && (contentBounds || dragBounds)
            ? (pos: { x: number; y: number }) => {
                  if (contentBounds) {
                      return {
                          x: Math.max(contentBounds.minX + radius, Math.min(contentBounds.maxX - radius, pos.x)),
                          y: Math.max(contentBounds.minY + radius, Math.min(contentBounds.maxY - radius, pos.y)),
                      };
                  }
                  if (dragBounds) {
                      return {
                          x: Math.max(radius, Math.min(dragBounds.width - radius, pos.x)),
                          y: Math.max(radius, Math.min(dragBounds.height - radius, pos.y)),
                      };
                  }
                  return pos;
              }
            : undefined;

    const fill = isFirst ? editorColors.vertexFirst : isActive ? editorColors.vertexActive : editorColors.vertex;
    const stroke = isHovered && !readonly ? editorColors.strokeHover : fill;

    return (
        <Circle
            x={vertex.x}
            y={vertex.y}
            radius={radius}
            fill={fill}
            stroke={stroke}
            strokeWidth={strokeWidth}
            draggable={draggable && !!onDragMove}
            cursor={!readonly ? "pointer" : undefined}
            dragBoundFunc={dragBoundFunc}
            onDragMove={
                onDragMove
                    ? (e) => {
                          const pos = e.target.position();
                          onDragMove(pos.x, pos.y);
                      }
                    : undefined
            }
            onDragEnd={onDragEnd}
            onClick={onClick}
            onTap={onClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            shadowBlur={isHovered || isActive ? 10 : 0}
            shadowColor="rgba(0,0,0,0.4)"
            shadowOpacity={0.5}
        />
    );
};
