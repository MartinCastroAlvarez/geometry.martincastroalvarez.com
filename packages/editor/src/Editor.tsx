import { useCallback, useEffect, useMemo, useState } from "react";
import { Stage, Layer } from "react-konva";
import { Point, Polygon } from "@geometry/domain";
import { EditorModel, type EditorVertex } from "./models";
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
function findCycles(
    vertices: EditorVertex[],
    edges: [number, number][]
): EditorVertex[][] {
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
}

/** Signed area of a polygon (positive = counterclockwise) */
function signedArea(vertices: EditorVertex[]): number {
    let area = 0;
    const n = vertices.length;
    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        area += vertices[i].x * vertices[j].y - vertices[j].x * vertices[i].y;
    }
    return area / 2;
}

/** Check if cycle A is inside cycle B (point-in-polygon) */
function isInside(a: EditorVertex[], b: EditorVertex[]): boolean {
    if (a.length === 0 || b.length === 0) return false;
    const p = new Point(a[0].x, a[0].y);
    const poly = EditorModel.toDomain(b);
    return poly.contains(p);
}

export function Editor({
    boundary,
    obstacles,
    width,
    height,
    onChange,
    readonly = false,
}: EditorProps) {
    const [vertices, setVertices] = useState<EditorVertex[]>(() => [
        ...EditorModel.fromDomain(boundary),
        ...obstacles.flatMap((o) => EditorModel.fromDomain(o)),
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

    useEffect(() => {
        const bv = EditorModel.fromDomain(boundary);
        const hv = obstacles.flatMap((o) => EditorModel.fromDomain(o));
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
        const boundaryPoly = EditorModel.toDomain(boundaryCycle);
        const holePolys: Polygon[] = [];
        for (let i = 1; i < withArea.length; i++) {
            if (isInside(withArea[i].cycle, boundaryCycle)) {
                holePolys.push(EditorModel.toDomain(withArea[i].cycle));
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

    const handleStageClick = useCallback(
        (e: { target: { getStage: () => unknown } }) => {
            if (readonly) return;
            const stage = e.target.getStage() as {
                getPointerPosition: () => { x: number; y: number } | null;
            } | null;
            const pos = stage?.getPointerPosition?.();
            if (!pos) return;
            const newVertex: EditorVertex = {
                id: `v-${Date.now()}-${pos.x}-${pos.y}`,
                x: pos.x,
                y: pos.y,
            };
            setVertices((prev) => [...prev, newVertex]);
            setActiveIndex(null);
        },
        [readonly]
    );

    const handleVertexClick = useCallback(
        (index: number) => {
            if (readonly) return;
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
                setActiveIndex(null);
                return;
            }
            setActiveIndex(index);
        },
        [readonly, activeIndex, degree, edges]
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
            style={{
                border: "2px solid rgba(100, 116, 139, 0.6)",
                borderRadius: 12,
                overflow: "hidden",
                background: "rgba(30, 41, 59, 0.5)",
            }}
        >
            <Stage
                width={width}
                height={height}
                onClick={handleStageClick}
                style={{ cursor, borderRadius: 10 }}
            >
                <Layer>
                    {allEdges.map(({ start, end, closed }, i) => (
                        <Edge
                            key={`edge-${i}`}
                            start={start}
                            end={end}
                            closed={closed}
                            dashed={!closed}
                        />
                    ))}
                    {vertices.map((v, i) => (
                        <Vertex
                            key={v.id}
                            vertex={v}
                            isFirst={false}
                            isActive={activeIndex === i}
                            onClick={() => handleVertexClick(i)}
                            onDragMove={!readonly ? (x, y) => handleVertexDrag(i, x, y) : undefined}
                            draggable={!readonly}
                        />
                    ))}
                </Layer>
            </Stage>
        </div>
    );
}
