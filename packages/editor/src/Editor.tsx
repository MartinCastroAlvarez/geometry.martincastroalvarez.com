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
import { useLocale } from "@geometry/i18n";
import { Container, Tooltip } from "@geometry/ui";
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
    onValidate?: () => void;
    onSubmit?: () => void;
    /** When true, Validate and Submit in the toolbar are disabled (e.g. while a request is pending). */
    disabled?: boolean;
}

export const Editor = ({
    width,
    height,
    onChange,
    onVerticesChange,
    onZoomOut,
    onClean,
    onZoomIn,
    onValidate,
    onSubmit,
    disabled = false,
}: EditorProps) => {
    const [vertices, setVertices] = useState<EditorVertex[]>(() => []);
    const [edges, setEdges] = useState<[number, number][]>(() => []);
    const [activeIndex, setActiveIndex] = useState<number | null>(null);
    const [selectedEdgeIndex, setSelectedEdgeIndex] = useState<number | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const { t } = useLocale();

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

    const ZOOM_MIN = 0.25;
    const ZOOM_MAX = 4;
    const ZOOM_STEP = 1.2;
    const [scale, setScale] = useState(1);
    const handleZoomIn = useCallback(() => {
        setScale((s) => Math.min(ZOOM_MAX, s * ZOOM_STEP));
        onZoomIn?.();
    }, [onZoomIn]);
    const handleZoomOut = useCallback(() => {
        setScale((s) => Math.max(ZOOM_MIN, s / ZOOM_STEP));
        onZoomOut?.();
    }, [onZoomOut]);

    const handleClean = useCallback(() => {
        setVertices([]);
        setEdges([]);
        setActiveIndex(null);
        setSelectedEdgeIndex(null);
        onChange?.(emptyPolygon, []);
        onClean?.();
    }, [onChange, onClean]);

    const cycles = useMemo(() => findCycles(vertices, edges), [vertices, edges]);

    const allVerticesDegreeTwo = useMemo(() => {
        if (vertices.length === 0) return false;
        const degree = (i: number) => edges.filter(([a, b]) => a === i || b === i).length;
        return vertices.every((_, i) => degree(i) === 2);
    }, [vertices, edges]);

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
        // Defer parent notification to next frame so adding a point doesn't block the next click
        const frameId = requestAnimationFrame(() => {
            lastNotifiedRef.current = { boundary: b, obstacles: o };
            onChange?.(b ?? emptyPolygon, o);
        });
        return () => cancelAnimationFrame(frameId);
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

    // When zoomed out (scale < 1), expand the canvas so the polygon can extend further; limit grows with zoom-out.
    const stageWidth = scale <= 1 ? effectiveWidth / scale : effectiveWidth;
    const stageHeight = scale <= 1 ? effectiveHeight / scale : effectiveHeight;
    const dragBounds = useMemo(
        () => ({ width: stageWidth, height: stageHeight }),
        [stageWidth, stageHeight]
    );

    return (
        <div
            tabIndex={-1}
            role="application"
            aria-label="Geometry editor"
            onKeyDown={handleKeyDown}
            style={{
                outline: "none",
                display: "flex",
                flexDirection: "column",
                height: "100%",
                minHeight: 0,
            }}
        >
            <div
                style={{
                    flex: "1 1 0",
                    minHeight: 0,
                    overflow: "hidden",
                    display: "flex",
                    flexDirection: "column",
                }}
            >
                <div
                    ref={containerRef}
                    style={{ flex: 1, minHeight: 0, overflow: "hidden" }}
                >
                    <Container name="geometry-editor-canvas">
                        {/* Canvas: grid fixed; only Stage (vertices/edges) scales with zoom */}
                <div
                    className="opacity-60 overflow-hidden rounded-[10px]"
                    style={{
                        position: "relative",
                        width: "100%",
                        height: effectiveHeight,
                        minHeight: height,
                    }}
                >
                        <Grid width={effectiveWidth} height={effectiveHeight} style={{ left: 0, top: 0, zIndex: 0 }} />
                        {vertices.length === 0 && (
                            <Tooltip
                                width={effectiveWidth}
                                height={effectiveHeight}
                                z={1}
                            >
                                {t("editor.clickToDrawPolygon")}
                            </Tooltip>
                        )}
                        {vertices.length === 2 && (
                            <Tooltip
                                width={effectiveWidth}
                                height={effectiveHeight}
                                z={1}
                                right
                                bottom
                            >
                                {t("editor.atLeastThreePointsRequired")}
                            </Tooltip>
                        )}
                        {vertices.length >= 3 && !allVerticesDegreeTwo && (
                            <Tooltip
                                width={effectiveWidth}
                                height={effectiveHeight}
                                z={1}
                                right
                                bottom
                            >
                                {t("editor.closePolygonToContinue")}
                            </Tooltip>
                        )}
                        {vertices.length > 0 && allVerticesDegreeTwo && (
                            <Tooltip
                                width={effectiveWidth}
                                height={effectiveHeight}
                                z={1}
                                right
                                bottom
                            >
                                {t("editor.nextStepValidateSubmit")}
                            </Tooltip>
                        )}
                        <div
                            style={{
                                position: "absolute",
                                left: 0,
                                top: 0,
                                width: stageWidth,
                                height: stageHeight,
                                transform: `scale(${scale})`,
                                transformOrigin: "0 0",
                                zIndex: 2,
                            }}
                        >
                            <Stage
                                width={stageWidth}
                                height={stageHeight}
                                onClick={handleStageClick}
                                style={{
                                    position: "relative",
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
                    </div>
                    </Container>
                </div>
            </div>
            {vertices.length > 0 && (
                <div style={{ flexShrink: 0, padding: "0.75rem 0" }}>
                    <Container middle spaced right name="geometry-editor-toolbar">
                        <EditorToolbar
                            onZoomOut={handleZoomOut}
                            onClean={handleClean}
                            onZoomIn={handleZoomIn}
                            onValidate={allVerticesDegreeTwo ? onValidate : undefined}
                            onSubmit={allVerticesDegreeTwo ? onSubmit : undefined}
                            disabled={disabled}
                        />
                    </Container>
                </div>
            )}
        </div>
    );
};
