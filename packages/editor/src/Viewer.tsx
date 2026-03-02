/**
 * Display-only viewer for an ArtGallery: grid background and edges (no vertices).
 * When artGallery is null or undefined, the grid is shown but no polygon (empty state).
 * When interactive is true, pan is enabled and a ViewerToolbar is shown for mode (polygon vs stitching).
 * Default mode: boundary and obstacles only. Stitching mode: only the stitches (bridge edges from API).
 */

import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { Stage, Layer } from "react-konva";
import type { ArtGallery } from "@geometry/domain";
import { Container, useDevice } from "@geometry/ui";
import { artGalleryToEditorState, stitchesToEditorState } from "./adapters";
import type { EditorVertex } from "./types";
import { Edge } from "./Edge";
import { Grid } from "./Grid";
import { ViewerMode } from "./ViewerMode";
import { ViewerToolbar } from "./ViewerToolbar";

const FIT_PADDING = 16;

export interface ViewerProps {
    /** Art gallery to display; when null or undefined, grid is shown with no polygon. */
    artGallery?: ArtGallery | null;
    /** Size (height) of the canvas in pixels. Width is 100% of the container. */
    size: number;
    /** When true, pan and interaction are enabled. Default false. */
    interactive?: boolean;
}

export const Viewer = ({
    artGallery,
    size,
    interactive = false,
}: ViewerProps) => {
    return (
        <ViewerInner
            artGallery={artGallery}
            size={size}
            interactive={interactive}
        />
    );
};

const EMPTY_STATE: {
    vertices: EditorVertex[];
    edges: [number, number][];
    stitchEdgeStartIndex: number;
} = { vertices: [], edges: [], stitchEdgeStartIndex: 0 };

function computeFitTransform(
    vertices: EditorVertex[],
    stageWidth: number,
    stageHeight: number
): { scale: number; x: number; y: number } | null {
    if (vertices.length === 0 || stageWidth <= 0 || stageHeight <= 0) return null;
    let minX = Infinity,
        minY = Infinity,
        maxX = -Infinity,
        maxY = -Infinity;
    for (const v of vertices) {
        minX = Math.min(minX, v.x);
        minY = Math.min(minY, v.y);
        maxX = Math.max(maxX, v.x);
        maxY = Math.max(maxY, v.y);
    }
    const contentW = maxX - minX || 1;
    const contentH = maxY - minY || 1;
    const usableW = Math.max(stageWidth - 2 * FIT_PADDING, 1);
    const usableH = Math.max(stageHeight - 2 * FIT_PADDING, 1);
    const scale = Math.min(usableW / contentW, usableH / contentH, 20);
    const x = stageWidth / 2 - ((minX + maxX) / 2) * scale;
    const y = stageHeight / 2 - ((minY + maxY) / 2) * scale;
    return { scale, x, y };
}

const ViewerInner = ({
    artGallery,
    size,
    interactive = false,
}: {
    artGallery?: ArtGallery | null;
    size: number;
    interactive?: boolean;
}) => {
    const readonly = !interactive;
    const containerRef = useRef<HTMLDivElement>(null);
    const stageWrapperRef = useRef<HTMLDivElement>(null);
    const [containerSize, setContainerSize] = useState({ width: 0, height: size });
    const [pan, setPan] = useState({ x: 0, y: 0 });
    const [isPanning, setIsPanning] = useState(false);
    const panStartRef = useRef<{ clientX: number; clientY: number; panX: number; panY: number } | null>(null);
    const scaleRef = useRef(1);
    const [scale] = useState(1);
    scaleRef.current = scale;

    const effectiveWidth = Math.max(containerSize.width, 1);
    const effectiveHeight = Math.max(containerSize.height, size);
    const stageWidth = scale <= 1 ? effectiveWidth / scale : effectiveWidth;
    const stageHeight = scale <= 1 ? effectiveHeight / scale : effectiveHeight;

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

    const [mode, setMode] = useState<ViewerMode>(ViewerMode.Default);
    const { isMobile } = useDevice();

    const { vertices, edges, stitchEdgeStartIndex } = useMemo(() => {
        if (artGallery == null) return EMPTY_STATE;
        const base = artGalleryToEditorState(artGallery);
        if (mode === ViewerMode.Stitching && artGallery.stitches.length > 0) {
            const stitch = stitchesToEditorState(artGallery.stitches);
            const nBase = base.vertices.length;
            const mergedVertices = [...base.vertices, ...stitch.vertices];
            const mergedEdges: [number, number][] = [
                ...base.edges,
                ...stitch.edges.map(([a, b]) => [a + nBase, b + nBase] as [number, number]),
            ];
            return {
                vertices: mergedVertices,
                edges: mergedEdges,
                stitchEdgeStartIndex: base.edges.length,
            };
        }
        return {
            ...base,
            stitchEdgeStartIndex: base.edges.length,
        };
    }, [artGallery, mode]);

    const allEdges = useMemo(
        () =>
            edges
                .filter(([a, b]) => a < vertices.length && b < vertices.length)
                .map(([a, b], i) => ({
                    start: vertices[a],
                    end: vertices[b],
                    isStitch: i >= stitchEdgeStartIndex,
                })),
        [vertices, edges, stitchEdgeStartIndex]
    );

    const fitTransform = useMemo(
        () => (vertices.length > 0 ? computeFitTransform(vertices, stageWidth, stageHeight) : null),
        [vertices, stageWidth, stageHeight]
    );

    const layerScale = fitTransform ? fitTransform.scale : 1;
    const layerX = fitTransform ? fitTransform.x : pan.x;
    const layerY = fitTransform ? fitTransform.y : pan.y;

    const handleStageMouseDown = useCallback(
        (e: { target: { getStage: () => unknown }; evt?: MouseEvent }) => {
            if (readonly) return;
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
        [readonly, pan.x, pan.y]
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

    useLayoutEffect(() => {
        if (containerRef.current) {
            const w = containerRef.current.clientWidth;
            const h = containerRef.current.clientHeight;
            if (w > 0 && h > 0) setContainerSize((prev) => (prev.width ? prev : { width: w, height: h }));
        }
    }, []);

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                height: "100%",
                minHeight: 0,
                width: "100%",
            }}
        >
            {interactive && (
                <div style={{ flexShrink: 0, padding: "0 0 0.75rem 0" }}>
                    <Container middle spaced name="geometry-viewer-toolbar">
                        <ViewerToolbar mode={mode} onModeChange={setMode} alignRight={!isMobile} />
                    </Container>
                </div>
            )}
            <div
                ref={containerRef}
                style={{ flex: 1, minHeight: 0, overflow: "hidden", width: "100%" }}
            >
                <div
                    className="geometry-viewer-canvas w-full overflow-hidden rounded-[10px]"
                    style={{
                        position: "relative",
                        width: "100%",
                        height: effectiveHeight,
                        minHeight: size,
                    }}
                >
                    <Grid
                        width={effectiveWidth}
                        height={effectiveHeight}
                    />
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
                            cursor: readonly ? "default" : isPanning ? "grabbing" : "grab",
                        }}
                    >
                        <Stage
                            width={stageWidth}
                            height={stageHeight}
                            onMouseDown={handleStageMouseDown}
                            style={{ position: "relative", borderRadius: 10 }}
                        >
                            <Layer
                                x={layerX}
                                y={layerY}
                                scaleX={layerScale}
                                scaleY={layerScale}
                            >
                                {allEdges.map(({ start, end, isStitch }, i) => (
                                    <Edge
                                        key={`edge-${i}`}
                                        start={start}
                                        end={end}
                                        edgeIndex={i}
                                        muted={mode === ViewerMode.Stitching && isStitch}
                                        scale={scale * layerScale}
                                    />
                                ))}
                            </Layer>
                        </Stage>
                    </div>
                </div>
            </div>
        </div>
    );
};
