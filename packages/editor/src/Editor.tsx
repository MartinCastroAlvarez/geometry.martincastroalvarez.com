/**
 * Geometry editor canvas: vertices and edges. Mode-driven interaction:
 * - Add: click empty → add vertex; click vertex → select / create edge.
 * - Connect: same but new vertex is auto-selected so next click connects.
 * - Move: drag on canvas to pan the view; geometry unchanged.
 * - Erase: click vertex or edge → remove it.
 * Zoom and clean are internal; only onChange (geometry), onValidate, onSubmit are exposed.
 */

import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { Stage, Layer } from "react-konva";
import { ArtGallery, Polygon } from "@geometry/domain";
import { useLocale } from "@geometry/i18n";
import { Container, Tooltip } from "@geometry/ui";
import type { EditorVertex } from "./types";
import { artGalleryToEditorState, editorVerticesToPolygon } from "./adapters";
import { findCycles, signedArea, isInside, polyEquals, polyArrayEquals } from "./utils";
import { Edge } from "./Edge";
import { Grid } from "./Grid";
import { Vertex } from "./Vertex";
import { EditorToolbar } from "./EditorToolbar";
import { EditorMode } from "./EditorMode";

export interface EditorProps {
    width: number;
    height: number;
    /** Current gallery (boundary + obstacles + guards). Editor initializes and syncs from this; onChange reports updates. */
    gallery: ArtGallery;
    /** Called with the updated ArtGallery or null when the canvas is cleared. */
    onChange?: (gallery: ArtGallery | null) => void;
}

export const Editor = ({
    width,
    height,
    gallery,
    onChange,
}: EditorProps) => {
    const stateFromGallery = useMemo(
        () => artGalleryToEditorState(gallery),
        [gallery]
    );
    const [vertices, setVertices] = useState<EditorVertex[]>(() => stateFromGallery.vertices);
    const [edges, setEdges] = useState<[number, number][]>(() => stateFromGallery.edges);
    const [activeIndex, setActiveIndex] = useState<number | null>(null);
    const [selectedEdgeIndex, setSelectedEdgeIndex] = useState<number | null>(null);
    const [mode, setMode] = useState<EditorMode>(EditorMode.Connect);
    const [pan, setPan] = useState({ x: 0, y: 0 });
    const [isPanning, setIsPanning] = useState(false);
    const panStartRef = useRef<{ clientX: number; clientY: number; panX: number; panY: number } | null>(null);
    const scaleRef = useRef(1);
    const containerRef = useRef<HTMLDivElement>(null);
    const stageWrapperRef = useRef<HTMLDivElement>(null);
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

    const stageCursor =
        mode === EditorMode.Move ? (isPanning ? "grabbing" : "grab") : mode === EditorMode.Erase ? "cell" : "crosshair";
    useEffect(() => {
        const id = requestAnimationFrame(() => {
            const canvas = stageWrapperRef.current?.querySelector("canvas");
            if (canvas) {
                (canvas as HTMLCanvasElement).style.cursor = stageCursor;
            }
        });
        return () => cancelAnimationFrame(id);
    }, [stageCursor]);

    const effectiveWidth = containerSize.width;
    const effectiveHeight = containerSize.height;

    const ZOOM_MIN = 0.25;
    const ZOOM_MAX = 4;
    const ZOOM_STEP = 1.2;
    const [scale, setScale] = useState(1);
    scaleRef.current = scale;
    const handleZoomIn = useCallback(() => {
        setScale((s) => Math.min(ZOOM_MAX, s * ZOOM_STEP));
    }, []);
    const handleZoomOut = useCallback(() => {
        setScale((s) => Math.max(ZOOM_MIN, s / ZOOM_STEP));
    }, []);

    const handleClean = useCallback(() => {
        console.log("[Editor] action: clean → vertices=0, edges=0 → onChange(null)");
        setVertices([]);
        setEdges([]);
        setActiveIndex(null);
        setSelectedEdgeIndex(null);
        setPan({ x: 0, y: 0 });
        onChange?.(null);
    }, [onChange]);

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
    useLayoutEffect(() => {
        const b = boundary ?? undefined;
        const o = obstacles;
        const prev = lastNotifiedRef.current;
        const skip = prev && polyEquals(b ?? undefined, prev.boundary ?? undefined) && polyArrayEquals(o, prev.obstacles);
        const boundaryPts = b?.points?.length ?? 0;
        const willCallOnChange = !skip;
        const nextGallery = b == null || boundaryPts < 3 ? null : new ArtGallery(b, o, gallery.guards);
        console.log("[Editor] notify effect", {
            vertices: vertices.length,
            edges: edges.length,
            cycles: cycles.length,
            boundaryPts,
            skip: skip ? "yes (same as last)" : "no",
            willCallOnChange,
            nextGallery: willCallOnChange ? (nextGallery ? `ArtGallery(${boundaryPts} pts)` : "null") : "-",
        });
        if (skip) return;
        lastNotifiedRef.current = { boundary: b, obstacles: o };
        console.log("[Editor] onChange(", nextGallery ?? "null", ")");
        onChange?.(nextGallery);
    }, [boundary, obstacles, gallery.guards, onChange, vertices.length, edges.length, cycles.length]);

    const addVertexAt = useCallback(
        (pos: { x: number; y: number }, connectToNext: boolean) => {
            const newIndex = vertices.length;
            const newEdge = connectToNext && vertices.length >= 1 ? [vertices.length - 1, newIndex] as [number, number] : null;
            console.log("[Editor] action: addVertexAt", { pos, connectToNext, newIndex, newEdge, nextVertices: vertices.length + 1, nextEdges: edges.length + (newEdge ? 1 : 0) });
            setSelectedEdgeIndex(null);
            const newVertex: EditorVertex = {
                id: `v-${Date.now()}-${pos.x}-${pos.y}`,
                x: pos.x,
                y: pos.y,
            };
            setVertices((prev) => [...prev, newVertex]);
            if (newEdge) setEdges((prev) => [...prev, newEdge]);
            setActiveIndex(connectToNext ? newIndex : null);
            containerRef.current?.focus();
        },
        [vertices.length, edges.length]
    );

    const handleStageMouseDown = useCallback(
        (e: { target: { getStage: () => unknown }; evt?: MouseEvent }) => {
            if (mode !== EditorMode.Move) return;
            const stage = e.target.getStage();
            if (!stage || e.target !== stage) return;
            const evt = e.evt;
            if (!evt) return;
            evt.preventDefault();
            panStartRef.current = {
                clientX: evt.clientX,
                clientY: evt.clientY,
                panX: pan.x,
                panY: pan.y,
            };
            setIsPanning(true);
        },
        [mode, pan.x, pan.y]
    );

    useEffect(() => {
        if (!isPanning) return;
        const onMove = (e: MouseEvent) => {
            const start = panStartRef.current;
            if (!start) return;
            const s = scaleRef.current;
            setPan({
                x: start.panX + (e.clientX - start.clientX) / s,
                y: start.panY + (e.clientY - start.clientY) / s,
            });
        };
        const onUp = () => {
            panStartRef.current = null;
            setIsPanning(false);
        };
        window.addEventListener("mousemove", onMove);
        window.addEventListener("mouseup", onUp);
        return () => {
            window.removeEventListener("mousemove", onMove);
            window.removeEventListener("mouseup", onUp);
        };
    }, [isPanning]);

    const handleStageClick = useCallback(
        (e: { target: { getStage: () => unknown } }) => {
            if (mode === EditorMode.Erase || mode === EditorMode.Move) return;
            const stage = e.target.getStage();
            if (!stage || e.target !== stage) return;
            const pos = (stage as { getPointerPosition: () => { x: number; y: number } | null }).getPointerPosition?.();
            if (!pos) return;
            addVertexAt({ x: pos.x - pan.x, y: pos.y - pan.y }, mode === EditorMode.Connect);
        },
        [addVertexAt, mode, pan.x, pan.y]
    );

    const removeVertexAt = useCallback((index: number) => {
        console.log("[Editor] action: removeVertexAt", { index, nextVertices: vertices.length - 1 });
        setVertices((prev) => prev.filter((_, i) => i !== index));
        setEdges((prev) =>
            prev
                .filter(([a, b]) => a !== index && b !== index)
                .map(([a, b]) => [
                    a > index ? a - 1 : a,
                    b > index ? b - 1 : b,
                ] as [number, number])
        );
        setActiveIndex(null);
        setSelectedEdgeIndex(null);
        containerRef.current?.focus();
    }, [vertices.length]);

    const removeEdgeAt = useCallback((edgeIndex: number) => {
        console.log("[Editor] action: removeEdgeAt", { edgeIndex, edge: edges[edgeIndex], nextEdges: edges.length - 1 });
        setEdges((prev) => prev.filter((_, i) => i !== edgeIndex));
        setSelectedEdgeIndex(null);
        setActiveIndex(null);
        containerRef.current?.focus();
    }, [edges]);

    const handleVertexClick = useCallback(
        (index: number) => {
            if (mode === EditorMode.Erase) {
                removeVertexAt(index);
                return;
            }
            if (mode === EditorMode.Move) return;
            setSelectedEdgeIndex(null);
            if (activeIndex === index) {
                console.log("[Editor] action: vertexClick deselect", { index });
                setActiveIndex(null);
                return;
            }
            if (activeIndex !== null) {
                const key = (a: number, b: number) => `${Math.min(a, b)}-${Math.max(a, b)}`;
                const existing = new Set(edges.map(([a, b]) => key(a, b)));
                const edgeKey = key(activeIndex, index);
                if (!existing.has(edgeKey)) {
                    console.log("[Editor] action: vertexClick add edge", { from: activeIndex, to: index, edgeKey, nextEdges: edges.length + 1 });
                    setEdges((prev) => [...prev, [activeIndex, index]]);
                } else {
                    console.log("[Editor] action: vertexClick edge exists", { from: activeIndex, to: index, edgeKey });
                }
            }
            setActiveIndex(index);
            containerRef.current?.focus();
        },
        [mode, activeIndex, edges, removeVertexAt]
    );

    const handleEdgeClick = useCallback(
        (edgeIndex: number, x: number, y: number) => {
            if (mode === EditorMode.Erase) {
                removeEdgeAt(edgeIndex);
                return;
            }
            if (mode === EditorMode.Move) return;
            if (selectedEdgeIndex === edgeIndex) {
                const [a, b] = edges[edgeIndex];
                const newIndex = vertices.length;
                console.log("[Editor] action: edgeClick split edge", { edgeIndex, edge: [a, b], newVertexIndex: newIndex, nextVertices: vertices.length + 1, nextEdges: edges.length + 1 });
                const wx = x - pan.x;
                const wy = y - pan.y;
                const newVertex: EditorVertex = {
                    id: `v-${Date.now()}-${wx}-${wy}`,
                    x: wx,
                    y: wy,
                };
                setVertices((v) => [...v, newVertex]);
                setEdges((e) => {
                    const next = e.filter((_, i) => i !== edgeIndex);
                    next.push([a, newIndex], [newIndex, b]);
                    return next;
                });
                setSelectedEdgeIndex(null);
                setActiveIndex(newIndex);
            } else {
                console.log("[Editor] action: edgeClick select edge", { edgeIndex });
                setSelectedEdgeIndex(edgeIndex);
                setActiveIndex(null);
            }
            containerRef.current?.focus();
        },
        [mode, selectedEdgeIndex, edges, vertices.length, removeEdgeAt, pan.x, pan.y]
    );

    const handleVertexDrag = useCallback((index: number, x: number, y: number) => {
        setVertices((prev) => {
            const next = [...prev];
            next[index] = { ...next[index], x, y };
            return next;
        });
    }, []);

    const handleVertexDragEnd = useCallback((index: number) => {
        console.log("[Editor] action: vertexDragEnd", { index, note: "vertices updated → notify effect will run" });
        setActiveIndex(index);
        containerRef.current?.focus();
    }, []);

    const removeActiveVertex = useCallback(() => {
        if (activeIndex === null) return;
        const idx = activeIndex;
        console.log("[Editor] action: removeActiveVertex", { index: idx, nextVertices: vertices.length - 1 });
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
    }, [activeIndex, vertices.length]);

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
                    <Container name="geometry-editor-canvas" middle>
                        {/* Canvas: grid fixed; only Stage (vertices/edges) scales with zoom */}
                <div
                    className="overflow-hidden rounded-[10px]"
                    style={{
                        position: "relative",
                        width: "100%",
                        height: effectiveHeight,
                        minHeight: height,
                    }}
                >
                        <Grid
                            width={effectiveWidth}
                            height={effectiveHeight}
                        />
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
                            ref={stageWrapperRef}
                            style={{
                                position: "absolute",
                                left: 0,
                                top: 0,
                                width: stageWidth,
                                height: stageHeight,
                                transform: `scale(${scale})`,
                                transformOrigin: "0 0",
                                zIndex: 2,
                                cursor: stageCursor,
                            }}
                        >
                            <Stage
                                width={stageWidth}
                                height={stageHeight}
                                onClick={handleStageClick}
                                onMouseDown={handleStageMouseDown}
                                style={{
                                    position: "relative",
                                    borderRadius: 10,
                                }}
                            >
                                <Layer x={pan.x} y={pan.y}>
                                    {allEdges.map(({ start, end }, i) => (
                                        <Edge
                                            key={`edge-${i}`}
                                            start={start}
                                            end={end}
                                            edgeIndex={i}
                                            selected={selectedEdgeIndex === i}
                                            onClick={handleEdgeClick}
                                            scale={scale}
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
                                            scale={scale}
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
                            mode={mode}
                            onModeChange={setMode}
                            onZoomOut={handleZoomOut}
                            onClean={handleClean}
                            onZoomIn={handleZoomIn}
                        />
                    </Container>
                </div>
            )}
        </div>
    );
};
