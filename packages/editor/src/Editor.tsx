/**
 * Geometry editor canvas: vertices and edges. Simple interaction model:
 * 1. Click empty space → add vertex
 * 2. Click vertex → make it active
 * 3. Click another vertex when one is active → create edge
 * 4. Click edge → make edge active
 * 5. Click active edge → split edge (new vertex, connect)
 * 6. Drag vertices
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Stage, Layer } from "react-konva";
import { Polygon } from "@geometry/domain";
import type { EditorVertex } from "./types";
import { editorVerticesToPolygon } from "./adapters";
import { findCycles, signedArea, isInside, polyEquals, polyArrayEquals, emptyPolygon } from "./utils";
import { Edge } from "./Edge";
import { Grid } from "./Grid";
import { Vertex } from "./Vertex";
import { EditorToolbar } from "./EditorToolbar";

export interface EditorProps {
    width: number;
    height: number;
    onChange?: (boundary?: Polygon, obstacles?: Polygon[]) => void;
    onVerticesChange?: (hasVertices: boolean) => void;
    onZoomOut?: () => void;
    onClean?: () => void;
    onZoomIn?: () => void;
}

export const Editor = ({
    width,
    height,
    onChange,
    onVerticesChange,
    onZoomOut,
    onClean,
    onZoomIn,
}: EditorProps) => {
    const [vertices, setVertices] = useState<EditorVertex[]>(() => []);
    const [edges, setEdges] = useState<[number, number][]>(() => []);
    const [activeIndex, setActiveIndex] = useState<number | null>(null);
    const [selectedEdgeIndex, setSelectedEdgeIndex] = useState<number | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    const [containerSize, setContainerSize] = useState({ width, height });
    useEffect(() => {
        const el = containerRef.current;
        if (!el) return;
        const ro = new ResizeObserver((entries) => {
            const { width: w, height: h } = entries[0]?.contentRect ?? {};
            if (w != null && h != null && w > 0 && h > 0) {
                setContainerSize({ width: w, height: h });
            }
        });
        ro.observe(el);
        return () => ro.disconnect();
    }, []);

    const effectiveWidth = containerSize.width;
    const effectiveHeight = containerSize.height;

    const handleClean = useCallback(() => {
        setVertices([]);
        setEdges([]);
        setActiveIndex(null);
        setSelectedEdgeIndex(null);
        onChange?.(emptyPolygon, []);
        onClean?.();
    }, [onChange, onClean]);

    const cycles = useMemo(() => findCycles(vertices, edges), [vertices, edges]);

    const EMPTY_HOLES: Polygon[] = useMemo(() => [], []);
    const { boundary, obstacles } = useMemo(() => {
        if (cycles.length === 0) return { boundary: null, obstacles: EMPTY_HOLES };
        const withArea = cycles.map((c) => ({ cycle: c, area: Math.abs(signedArea(c)) }));
        withArea.sort((a, b) => b.area - a.area);
        const boundaryCycle = withArea[0].cycle;
        const boundaryVerts = signedArea(boundaryCycle) < 0 ? [...boundaryCycle].reverse() : boundaryCycle;
        const boundary = editorVerticesToPolygon(boundaryVerts);
        const obstacles: Polygon[] = [];
        for (let i = 1; i < withArea.length; i++) {
            if (isInside(withArea[i].cycle, boundaryCycle)) {
                const holeCycle = withArea[i].cycle;
                const holeVerts = signedArea(holeCycle) > 0 ? [...holeCycle].reverse() : holeCycle;
                obstacles.push(editorVerticesToPolygon(holeVerts));
            }
        }
        return { boundary, obstacles };
    }, [cycles, EMPTY_HOLES]);

    const lastNotifiedRef = useRef<{ boundary: Polygon | undefined; obstacles: Polygon[] } | null>(null);
    useEffect(() => {
        const b = boundary ?? undefined;
        const o = obstacles;
        const prev = lastNotifiedRef.current;
        if (prev && polyEquals(b, prev.boundary) && polyArrayEquals(o, prev.obstacles)) return;
        lastNotifiedRef.current = { boundary: b, obstacles: o };
        onChange?.(b ?? emptyPolygon, o);
    }, [boundary, obstacles, onChange]);

    useEffect(() => {
        onVerticesChange?.(vertices.length > 0);
    }, [vertices.length, onVerticesChange]);

    const addVertexAt = useCallback((pos: { x: number; y: number }) => {
        setSelectedEdgeIndex(null);
        const newVertex: EditorVertex = {
            id: `v-${Date.now()}-${pos.x}-${pos.y}`,
            x: pos.x,
            y: pos.y,
        };
        const newIndex = vertices.length;
        setVertices((prev) => [...prev, newVertex]);
        setActiveIndex(newIndex);
        containerRef.current?.focus();
    }, [vertices.length]);

    const handleStageClick = useCallback(
        (e: { target: { getStage: () => unknown } }) => {
            const stage = e.target.getStage();
            if (!stage || e.target !== stage) return;
            const pos = (stage as { getPointerPosition: () => { x: number; y: number } | null }).getPointerPosition?.();
            if (!pos) return;
            addVertexAt(pos);
        },
        [addVertexAt]
    );

    const handleVertexClick = useCallback(
        (index: number) => {
            setSelectedEdgeIndex(null);
            if (activeIndex === index) {
                setActiveIndex(null);
                return;
            }
            if (activeIndex !== null) {
                const key = (a: number, b: number) => `${Math.min(a, b)}-${Math.max(a, b)}`;
                const existing = new Set(edges.map(([a, b]) => key(a, b)));
                if (!existing.has(key(activeIndex, index))) {
                    setEdges((prev) => [...prev, [activeIndex, index]]);
                }
            }
            setActiveIndex(index);
            containerRef.current?.focus();
        },
        [activeIndex, edges]
    );

    const handleEdgeClick = useCallback(
        (edgeIndex: number, x: number, y: number) => {
            if (selectedEdgeIndex === edgeIndex) {
                const [a, b] = edges[edgeIndex];
                const newVertex: EditorVertex = {
                    id: `v-${Date.now()}-${x}-${y}`,
                    x,
                    y,
                };
                const newIndex = vertices.length;
                setVertices((v) => [...v, newVertex]);
                setEdges((e) => {
                    const next = e.filter((_, i) => i !== edgeIndex);
                    next.push([a, newIndex], [newIndex, b]);
                    return next;
                });
                setSelectedEdgeIndex(null);
                setActiveIndex(newIndex);
            } else {
                setSelectedEdgeIndex(edgeIndex);
                setActiveIndex(null);
            }
            containerRef.current?.focus();
        },
        [selectedEdgeIndex, edges, vertices.length]
    );

    const handleVertexDrag = useCallback((index: number, x: number, y: number) => {
        setVertices((prev) => {
            const next = [...prev];
            next[index] = { ...next[index], x, y };
            return next;
        });
    }, []);

    const handleVertexDragEnd = useCallback((index: number) => {
        setActiveIndex(index);
        containerRef.current?.focus();
    }, []);

    const removeActiveVertex = useCallback(() => {
        if (activeIndex === null) return;
        const idx = activeIndex;
        setVertices((prev) => prev.filter((_, i) => i !== idx));
        setEdges((prev) =>
            prev
                .filter(([a, b]) => a !== idx && b !== idx)
                .map(([a, b]) => [
                    a > idx ? a - 1 : a,
                    b > idx ? b - 1 : b,
                ] as [number, number])
        );
        setActiveIndex(null);
    }, [activeIndex]);

    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent) => {
            if (activeIndex === null) return;
            if (e.key === "Delete" || e.key === "Backspace" || e.key === "Enter") {
                e.preventDefault();
                removeActiveVertex();
            }
        },
        [activeIndex, removeActiveVertex]
    );

    const allEdges = useMemo(() => {
        return edges
            .filter(([a, b]) => a < vertices.length && b < vertices.length)
            .map(([a, b]) => ({ start: vertices[a], end: vertices[b] }));
    }, [vertices, edges]);

    const dragBounds = useMemo(
        () => ({ width: effectiveWidth, height: effectiveHeight }),
        [effectiveWidth, effectiveHeight]
    );

    return (
        <div
            ref={containerRef}
            tabIndex={-1}
            role="application"
            aria-label="Geometry editor"
            onKeyDown={handleKeyDown}
            style={{
                position: "relative",
                width: "100%",
                minHeight: height,
                flexShrink: 0,
                borderRadius: 12,
                overflow: "visible",
                outline: "none",
            }}
        >
            {/* Canvas at 0.6 opacity so the rest of the UI stays in focus; overflow hidden so Stage stays within bounds */}
            <div className="opacity-60 overflow-hidden rounded-[10px]" style={{ position: "relative", width: "100%", height: "100%", minHeight: height }}>
                <Grid width={effectiveWidth} height={effectiveHeight} />
                <Stage
                    width={effectiveWidth}
                    height={effectiveHeight}
                    onClick={handleStageClick}
                    style={{
                        position: "relative",
                        zIndex: 1,
                        cursor: "crosshair",
                        borderRadius: 10,
                    }}
                >
                    <Layer>
                        {allEdges.map(({ start, end }, i) => (
                            <Edge
                                key={`edge-${i}`}
                                start={start}
                                end={end}
                                edgeIndex={i}
                                selected={selectedEdgeIndex === i}
                                onClick={handleEdgeClick}
                            />
                        ))}
                        {vertices.map((v, i) => (
                            <Vertex
                                key={v.id}
                                vertex={v}
                                index={i}
                                isActive={activeIndex === i}
                                onClick={handleVertexClick}
                                onDragMove={handleVertexDrag}
                                onDragEnd={handleVertexDragEnd}
                                draggable
                                dragBounds={dragBounds}
                            />
                        ))}
                    </Layer>
                </Stage>
            </div>
            {/* Floating toolbar: full opacity, bottom-right with margin, visible panel */}
            <div
                className="flex flex-row items-center gap-2 rounded-lg bg-slate-800/95 px-3 py-2 shadow-lg border border-slate-600/50"
                style={{ position: "absolute", bottom: 16, right: 16, zIndex: 50 }}
            >
                <EditorToolbar
                    onZoomOut={onZoomOut ?? (() => {})}
                    onClean={handleClean}
                    onZoomIn={onZoomIn ?? (() => {})}
                />
            </div>
        </div>
    );
};
