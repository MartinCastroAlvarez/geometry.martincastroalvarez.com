/**
 * Geometry editor canvas: boundary and obstacles as editable vertices and edges.
 *
 * Context: Uses react-konva Stage/Layer. State is vertices (EditorVertex[]) and edges ([number, number][]).
 * findCycles discovers closed polygons from the graph; largest by area is boundary, cycles inside it are holes.
 * Supports add vertex (click edge or stage), connect two vertices (click one then another), delete vertex/edge (key).
 * Calls onChange(boundaryPolygon, holePolygons) when cycles change.
 *
 * Example:
 *   <Editor boundary={poly} obstacles={[]} width={400} height={300} onChange={(b, o) => setGeometry(b, o)} />
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Stage, Layer } from "react-konva";
import { Polygon } from "@geometry/domain";
import type { EditorVertex } from "./types";
import { polygonToEditorVertices, editorVerticesToPolygon } from "./adapters";
import { findCycles, signedArea, isInside } from "./utils";
import { Edge } from "./Edge";
import { Grid } from "./Grid";
import { Vertex } from "./Vertex";

const STAGE_DOUBLE_CLICK_MS = 300;

function polyEquals(a: Polygon | undefined, b: Polygon | undefined): boolean {
    if (a === b) return true;
    if (!a || !b || a.points.length !== b.points.length) return false;
    return a.points.every((p, i) => p.x === b.points[i].x && p.y === b.points[i].y);
}

function polyArrayEquals(a: Polygon[], b: Polygon[]): boolean {
    if (a.length !== b.length) return false;
    return a.every((p, i) => polyEquals(p, b[i]));
}

const emptyPolygon = new Polygon([]);

export interface EditorProps {
    /** Boundary polygon; can be empty (no points). Defaults to empty polygon if omitted. */
    boundary?: Polygon;
    /** Obstacles (holes); can be empty array. Defaults to [] if omitted. */
    obstacles?: Polygon[];
    width: number;
    height: number;
    onChange?: (boundary?: Polygon, obstacles?: Polygon[]) => void;
    /** Called when the number of vertices changes; use to know if there is at least one point (e.g. to show toolbar). */
    onVerticesChange?: (hasVertices: boolean) => void;
}

export const Editor = ({
    boundary: boundaryProp = emptyPolygon,
    obstacles: obstaclesProp = [],
    width,
    height,
    onChange,
    onVerticesChange,
}: EditorProps) => {
    const boundaryNorm = boundaryProp ?? emptyPolygon;
    const obstaclesNorm = obstaclesProp ?? [];
    const [vertices, setVertices] = useState<EditorVertex[]>(() => [
        ...polygonToEditorVertices(boundaryNorm),
        ...obstaclesNorm.flatMap((o) => polygonToEditorVertices(o)),
    ]);
    const [edges, setEdges] = useState<[number, number][]>(() => {
        const e: [number, number][] = [];
        let idx = 0;
        for (const poly of [boundaryNorm, ...obstaclesNorm]) {
            const pts = poly.points ?? [];
            for (let i = 0; i < pts.length; i++) {
                const j = (i + 1) % pts.length;
                e.push([idx + i, idx + j]);
            }
            idx += pts.length;
        }
        return e;
    });
    const [activeIndex, setActiveIndex] = useState<number | null>(null);
    const [selectedEdgeIndex, setSelectedEdgeIndex] = useState<number | null>(null);
    /** Index of the tip of the current open chain; null when chain is closed or no chain. */
    const [lastVertexIndex, setLastVertexIndex] = useState<number | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const lastStageClickTimeRef = useRef<number>(0);
    const pendingStageSingleRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

    const SCROLL_PADDING = 80;
    const contentBounds = useMemo(() => {
        if (vertices.length === 0) {
            return {
                contentMinX: -SCROLL_PADDING,
                contentMinY: -SCROLL_PADDING,
                contentMaxX: effectiveWidth + SCROLL_PADDING,
                contentMaxY: effectiveHeight + SCROLL_PADDING,
                stageWidth: effectiveWidth,
                stageHeight: effectiveHeight,
            };
        }
        const xs = vertices.map((v) => v.x);
        const ys = vertices.map((v) => v.y);
        const contentMinX = Math.min(0, ...xs) - SCROLL_PADDING;
        const contentMinY = Math.min(0, ...ys) - SCROLL_PADDING;
        const contentMaxX = Math.max(effectiveWidth, ...xs) + SCROLL_PADDING;
        const contentMaxY = Math.max(effectiveHeight, ...ys) + SCROLL_PADDING;
        return {
            contentMinX,
            contentMinY,
            contentMaxX,
            contentMaxY,
            stageWidth: contentMaxX - contentMinX,
            stageHeight: contentMaxY - contentMinY,
        };
    }, [vertices, effectiveWidth, effectiveHeight]);

    const isFirstMountRef = useRef(true);
    useEffect(() => {
        if (isFirstMountRef.current) {
            isFirstMountRef.current = false;
            return;
        }
        const b = boundaryProp ?? emptyPolygon;
        const o = obstaclesProp ?? [];
        const bv = polygonToEditorVertices(b);
        const hv = o.flatMap((poly) => polygonToEditorVertices(poly));
        const all = [...bv, ...hv];
        const e: [number, number][] = [];
        let idx = 0;
        for (const poly of [b, ...o]) {
            const pts = poly.points ?? [];
            for (let i = 0; i < pts.length; i++) {
                const j = (i + 1) % pts.length;
                e.push([idx + i, idx + j]);
            }
            idx += pts.length;
        }
        setVertices(all);
        setEdges(e);
        setLastVertexIndex(null);
    }, [boundaryProp, obstaclesProp]);

    const degree = useMemo(() => {
        const d: number[] = Array(vertices.length).fill(0);
        for (const [a, b] of edges) {
            if (a < vertices.length && b < vertices.length) {
                d[a]++;
                d[b]++;
            }
        }
        return d;
    }, [vertices.length, edges]);

    const cycles = useMemo(() => findCycles(vertices, edges), [vertices, edges]);

    useEffect(() => {
        if (lastVertexIndex === null) return;
        const tipId = vertices[lastVertexIndex]?.id;
        if (!tipId) return;
        const isInCycle = cycles.some((c) => c.some((v) => v.id === tipId));
        if (isInCycle) setLastVertexIndex(null);
    }, [cycles, vertices, lastVertexIndex]);

    const EMPTY_HOLES: Polygon[] = useMemo(() => [], []);

    const { boundary, obstacles } = useMemo(() => {
        if (cycles.length === 0) return { boundary: null, obstacles: EMPTY_HOLES };
        const withArea = cycles.map((c) => ({ cycle: c, area: Math.abs(signedArea(c)) }));
        withArea.sort((a, b) => b.area - a.area);
        const boundaryCycle = withArea[0].cycle;
        const boundary = editorVerticesToPolygon(boundaryCycle);
        const obstacles: Polygon[] = [];
        for (let i = 1; i < withArea.length; i++) {
            if (isInside(withArea[i].cycle, boundaryCycle)) {
                obstacles.push(editorVerticesToPolygon(withArea[i].cycle));
            }
        }
        return { boundary, obstacles };
    }, [cycles, EMPTY_HOLES]);

    const lastNotifiedRef = useRef<{ boundary: Polygon | undefined; obstacles: Polygon[] } | null>(null);

    useEffect(() => {
        const b = boundary ?? undefined;
        const o = obstacles;

        const prev = lastNotifiedRef.current;
        const same =
            prev &&
            polyEquals(b, prev.boundary) &&
            polyArrayEquals(o, prev.obstacles);
        if (same) return;
        lastNotifiedRef.current = { boundary: b, obstacles: o };
        onChange?.(b, o);
    }, [boundary, obstacles, onChange]);

    useEffect(() => {
        onVerticesChange?.(vertices.length > 0);
    }, [vertices.length, onVerticesChange]);

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

    const addVertexAt = useCallback(
        (pos: { x: number; y: number }, connectToLast: boolean) => {
            setSelectedEdgeIndex(null);
            const newVertex: EditorVertex = {
                id: `v-${Date.now()}-${pos.x}-${pos.y}`,
                x: pos.x,
                y: pos.y,
            };
            const newIndex = vertices.length;
            setVertices((prev) => [...prev, newVertex]);
            const canConnect = connectToLast && lastVertexIndex !== null && degree[lastVertexIndex] < 2;
            if (canConnect) {
                setEdges((prev) => [...prev, [lastVertexIndex!, newIndex]]);
            }
            setLastVertexIndex(newIndex);
            setActiveIndex(newIndex);
            containerRef.current?.focus();
        },
        [vertices.length, lastVertexIndex, degree]
    );

    const handleStageClick = useCallback(
        (e: { target: { getStage: () => unknown } }) => {
            const stage = e.target.getStage();
            if (!stage || e.target !== stage) return;
            const pos = (stage as { getPointerPosition: () => { x: number; y: number } | null })
                .getPointerPosition?.();
            if (!pos) return;
            const now = Date.now();
            if (pendingStageSingleRef.current !== null) {
                clearTimeout(pendingStageSingleRef.current);
                pendingStageSingleRef.current = null;
            }
            if (now - lastStageClickTimeRef.current < STAGE_DOUBLE_CLICK_MS) {
                lastStageClickTimeRef.current = 0;
                addVertexAt(pos, false);
                return;
            }
            lastStageClickTimeRef.current = now;
            pendingStageSingleRef.current = setTimeout(() => {
                pendingStageSingleRef.current = null;
                addVertexAt(pos, true);
            }, STAGE_DOUBLE_CLICK_MS);
        },
        [addVertexAt]
    );

    const handleVertexClick = useCallback(
        (index: number) => {
            if (selectedEdgeIndex !== null) {
                const [a, b] = edges[selectedEdgeIndex];
                if (index === a || index === b) {
                    setSelectedEdgeIndex(null);
                    return;
                }
                if (degree[index] >= 1) {
                    setSelectedEdgeIndex(null);
                    return;
                }
                setEdges((prev) => {
                    const next = prev.filter((_, i) => i !== selectedEdgeIndex);
                    next.push([a, index], [index, b]);
                    return next;
                });
                setSelectedEdgeIndex(null);
                setActiveIndex(index);
                containerRef.current?.focus();
                return;
            }

            if (activeIndex === index) {
                setActiveIndex(null);
                return;
            }
            if (activeIndex !== null) {
                if (degree[activeIndex] >= 2 || degree[index] >= 2) {
                    setActiveIndex(null);
                    return;
                }
                const key = (a: number, b: number) =>
                    `${Math.min(a, b)}-${Math.max(a, b)}`;
                const existing = new Set(
                    edges.map(([a, b]) => key(a, b))
                );
                if (!existing.has(key(activeIndex, index))) {
                    const newEdges: [number, number][] = [...edges, [activeIndex, index]];
                    setEdges((prev) => [...prev, [activeIndex, index]]);
                    setLastVertexIndex(index);
                    const cyclesAfter = findCycles(vertices, newEdges);
                    const tipId = vertices[activeIndex]?.id;
                    const indexId = vertices[index]?.id;
                    if (tipId && indexId && cyclesAfter.some((c) => c.some((v) => v.id === tipId || v.id === indexId))) {
                        setLastVertexIndex(null);
                    }
                }
                setActiveIndex(index);
                containerRef.current?.focus();
                return;
            }
            setActiveIndex(index);
            containerRef.current?.focus();
        },
        [activeIndex, degree, edges, selectedEdgeIndex]
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

    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLDivElement>) => {
            if (e.key !== "Delete" && e.key !== "Backspace") return;

            if (selectedEdgeIndex !== null) {
                setEdges((prev) => prev.filter((_, i) => i !== selectedEdgeIndex));
                setSelectedEdgeIndex(null);
                e.preventDefault();
                return;
            }

            if (activeIndex !== null) {
                const idx = activeIndex;
                setEdges((prev) =>
                    prev
                        .filter(([a, b]) => a !== idx && b !== idx)
                        .map(([a, b]) => [
                            a > idx ? a - 1 : a,
                            b > idx ? b - 1 : b,
                        ] as [number, number])
                );
                setVertices((prev) => prev.filter((_, i) => i !== idx));
                setActiveIndex(null);
                setLastVertexIndex((prev) => {
                    if (prev === null) return null;
                    if (prev === idx) return null;
                    return prev > idx ? prev - 1 : prev;
                });
                e.preventDefault();
            }

            const SCROLL_STEP = 40;
            const el = scrollContainerRef.current;
            if (!el) return;
            const key = e.key as "ArrowUp" | "ArrowDown" | "ArrowLeft" | "ArrowRight";
            switch (key) {
                case "ArrowUp":
                    el.scrollBy({ top: -SCROLL_STEP, behavior: "smooth" });
                    break;
                case "ArrowDown":
                    el.scrollBy({ top: SCROLL_STEP, behavior: "smooth" });
                    break;
                case "ArrowLeft":
                    el.scrollBy({ left: -SCROLL_STEP, behavior: "smooth" });
                    break;
                case "ArrowRight":
                    el.scrollBy({ left: SCROLL_STEP, behavior: "smooth" });
                    break;
            }
        },
        [selectedEdgeIndex, activeIndex]
    );

    useEffect(() => () => {
        if (pendingStageSingleRef.current !== null) clearTimeout(pendingStageSingleRef.current);
    }, []);

    const cursor = "crosshair";

    const vertexContentBounds = useMemo(
        () => ({
            minX: contentBounds.contentMinX,
            minY: contentBounds.contentMinY,
            maxX: contentBounds.contentMaxX,
            maxY: contentBounds.contentMaxY,
        }),
        [
            contentBounds.contentMinX,
            contentBounds.contentMinY,
            contentBounds.contentMaxX,
            contentBounds.contentMaxY,
        ]
    );

    const allEdges = useMemo(() => {
        const result: { start: EditorVertex; end: EditorVertex; closed: boolean }[] = [];
        for (const [a, b] of edges) {
            if (a < vertices.length && b < vertices.length) {
                const inCycle = cycles.some((c) => {
                    const ids = new Set(c.map((v) => v.id));
                    return ids.has(vertices[a].id) && ids.has(vertices[b].id);
                });
                result.push({
                    start: vertices[a],
                    end: vertices[b],
                    closed: inCycle,
                });
            }
        }
        return result;
    }, [vertices, edges, cycles]);

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
                overflow: "hidden",
                outline: "none",
            }}
        >
            <div
                ref={scrollContainerRef}
                style={{
                    position: "absolute",
                    inset: 0,
                    overflow: "auto",
                    minWidth: contentBounds.stageWidth,
                    minHeight: contentBounds.stageHeight,
                }}
            >
                <Grid
                    width={contentBounds.stageWidth}
                    height={contentBounds.stageHeight}
                />
                <Stage
                    width={contentBounds.stageWidth}
                    height={contentBounds.stageHeight}
                    onClick={handleStageClick}
                    style={{
                        position: "relative",
                        zIndex: 1,
                        cursor,
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
                            isFirst={i === 0}
                            isActive={activeIndex === i}
                            onClick={handleVertexClick}
                            onDragMove={handleVertexDrag}
                            onDragEnd={handleVertexDragEnd}
                            draggable
                            contentBounds={vertexContentBounds}
                        />
                    ))}
                </Layer>
            </Stage>
            </div>
        </div>
    );
};
