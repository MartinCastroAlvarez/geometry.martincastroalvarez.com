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

import { useCallback, useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { Stage, Layer } from "react-konva";
import { Point, Polygon } from "@geometry/domain";
import type { EditorVertex } from "./types";
import { polygonToEditorVertices, editorVerticesToPolygon } from "./adapters";
import { Edge } from "./Edge";
import { Vertex } from "./Vertex";
export interface EditorProps {
    boundary: Polygon;
    obstacles: Polygon[];
    width: number;
    height: number;
    onChange?: (boundary?: Polygon, obstacles?: Polygon[]) => void;
    readonly?: boolean;
}

/** Find cycles (closed polygons) from vertices and edges. Returns ordered vertex arrays. */
const findCycles = (
    vertices: EditorVertex[],
    edges: [number, number][]
): EditorVertex[][] => {
    const n = vertices.length;
    const adj: number[][] = Array.from({ length: n }, () => []);
    for (const [a, b] of edges) {
        if (a >= 0 && a < n && b >= 0 && b < n && a !== b) {
            adj[a].push(b);
            adj[b].push(a);
        }
    }

    const cycles: EditorVertex[][] = [];
    const used = new Set<string>();

    for (let start = 0; start < n; start++) {
        if (adj[start].length !== 2) continue;

        const cycle: number[] = [];
        let v = start;
        let prev = -1;
        let valid = true;

        for (let i = 0; i <= n; i++) {
            if (i > 0 && v === start) break;
            cycle.push(v);
            const nexts = adj[v].filter((u) => u !== prev);
            if (nexts.length !== 1) {
                valid = false;
                break;
            }
            prev = v;
            v = nexts[0];
        }

        if (!valid || v !== start || cycle.length < 3) continue;

        const key = cycle.slice().sort((a, b) => a - b).join(",");
        if (used.has(key)) continue;
        used.add(key);

        cycles.push(cycle.map((i) => vertices[i]));
    }

    return cycles;
};

/** Signed area of a polygon (positive = counterclockwise) */
const signedArea = (vertices: EditorVertex[]): number => {
    let area = 0;
    const n = vertices.length;
    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        area += vertices[i].x * vertices[j].y - vertices[j].x * vertices[i].y;
    }
    return area / 2;
};

/** Check if cycle A is inside cycle B (point-in-polygon) */
const isInside = (a: EditorVertex[], b: EditorVertex[]): boolean => {
    if (a.length === 0 || b.length === 0) return false;
    const p = new Point(a[0].x, a[0].y);
    const poly = editorVerticesToPolygon(b);
    return poly.contains(p);
};

export const Editor = ({
    boundary,
    obstacles,
    width,
    height,
    onChange,
    readonly = false,
}: EditorProps) => {
    const [vertices, setVertices] = useState<EditorVertex[]>(() => [
        ...polygonToEditorVertices(boundary),
        ...obstacles.flatMap((o) => polygonToEditorVertices(o)),
    ]);
    const [edges, setEdges] = useState<[number, number][]>(() => {
        const e: [number, number][] = [];
        let idx = 0;
        for (const poly of [boundary, ...obstacles]) {
            const pts = poly.points;
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
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const bv = polygonToEditorVertices(boundary);
        const hv = obstacles.flatMap((o) => polygonToEditorVertices(o));
        const all = [...bv, ...hv];
        const e: [number, number][] = [];
        let idx = 0;
        for (const poly of [boundary, ...obstacles]) {
            const pts = poly.points;
            for (let i = 0; i < pts.length; i++) {
                const j = (i + 1) % pts.length;
                e.push([idx + i, idx + j]);
            }
            idx += pts.length;
        }
        setVertices(all);
        setEdges(e);
    }, [boundary, obstacles]);

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

    const { boundaryPoly, holePolys } = useMemo(() => {
        if (cycles.length === 0) return { boundaryPoly: null, holePolys: [] as Polygon[] };
        const withArea = cycles.map((c) => ({ cycle: c, area: Math.abs(signedArea(c)) }));
        withArea.sort((a, b) => b.area - a.area);
        const boundaryCycle = withArea[0].cycle;
        const boundaryPoly = editorVerticesToPolygon(boundaryCycle);
        const holePolys: Polygon[] = [];
        for (let i = 1; i < withArea.length; i++) {
            if (isInside(withArea[i].cycle, boundaryCycle)) {
                holePolys.push(editorVerticesToPolygon(withArea[i].cycle));
            }
        }
        return { boundaryPoly, holePolys };
    }, [cycles]);

    const notifyChange = useCallback(
        (b?: Polygon, o?: Polygon[]) => {
            onChange?.(b, o);
        },
        [onChange]
    );

    useEffect(() => {
        if (boundaryPoly) {
            notifyChange(boundaryPoly, holePolys);
        } else {
            notifyChange(undefined, undefined);
        }
    }, [boundaryPoly, holePolys, notifyChange]);

    const handleEdgeClick = useCallback(
        (edgeIndex: number, x: number, y: number) => {
            if (readonly) return;
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
        [readonly, selectedEdgeIndex, edges, vertices.length]
    );

    const handleStageClick = useCallback(
        (e: { target: { getStage: () => unknown } }) => {
            if (readonly) return;
            const stage = e.target.getStage();
            if (!stage || e.target !== stage) return;
            setSelectedEdgeIndex(null);
            const pos = (stage as { getPointerPosition: () => { x: number; y: number } | null })
                .getPointerPosition?.();
            if (!pos) return;
            const newVertex: EditorVertex = {
                id: `v-${Date.now()}-${pos.x}-${pos.y}`,
                x: pos.x,
                y: pos.y,
            };
            const newIndex = vertices.length;
            setVertices((prev) => [...prev, newVertex]);
            setActiveIndex(newIndex);
            containerRef.current?.focus();
        },
        [readonly, vertices.length]
    );

    const handleVertexClick = useCallback(
        (index: number) => {
            if (readonly) return;

            if (selectedEdgeIndex !== null) {
                const [a, b] = edges[selectedEdgeIndex];
                if (index === a || index === b) {
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
                    setEdges((prev) => [...prev, [activeIndex, index]]);
                }
                setActiveIndex(index);
                containerRef.current?.focus();
                return;
            }
            setActiveIndex(index);
            containerRef.current?.focus();
        },
        [readonly, activeIndex, degree, edges, selectedEdgeIndex]
    );

    const handleVertexDrag = useCallback(
        (index: number, x: number, y: number) => {
            if (readonly) return;
            setVertices((prev) => {
                const next = [...prev];
                next[index] = { ...next[index], x, y };
                return next;
            });
        },
        [readonly]
    );

    const handleKeyDown = useCallback(
        (e: KeyboardEvent<HTMLDivElement>) => {
            if (readonly) return;
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
                e.preventDefault();
            }
        },
        [readonly, selectedEdgeIndex, activeIndex]
    );

    const cursor = readonly ? "default" : "crosshair";

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
                width,
                height,
                minWidth: width,
                minHeight: height,
                flexShrink: 0,
                borderRadius: 12,
                overflow: "hidden",
                outline: "none",
            }}
        >
            <div
                style={{
                    position: "absolute",
                    inset: 0,
                    backgroundColor: "rgba(2, 6, 23, 0.85)",
                    backgroundImage: `
                        linear-gradient(to right, rgba(255, 255, 255, 0.08) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(255, 255, 255, 0.08) 1px, transparent 1px)
                    `,
                    backgroundSize: "24px 24px",
                }}
            />
            <Stage
                width={width}
                height={height}
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
                            selected={selectedEdgeIndex === i}
                            onClick={!readonly ? (x, y) => handleEdgeClick(i, x, y) : undefined}
                            readonly={readonly}
                        />
                    ))}
                    {vertices.map((v, i) => (
                        <Vertex
                            key={v.id}
                            vertex={v}
                            isFirst={i === 0}
                            isActive={activeIndex === i}
                            onClick={() => handleVertexClick(i)}
                            onDragMove={!readonly ? (x, y) => handleVertexDrag(i, x, y) : undefined}
                            onDragEnd={
                                !readonly
                                    ? () => {
                                          setActiveIndex(i);
                                          containerRef.current?.focus();
                                      }
                                    : undefined
                            }
                            draggable={!readonly}
                            dragBounds={readonly ? undefined : { width, height }}
                            readonly={readonly}
                        />
                    ))}
                </Layer>
            </Stage>
        </div>
    );
};
