# Computational Geometry Lab

A computational geometry library and playground for implementing art gallery algorithms from first principles.

## Purpose

- **Art Gallery Problem**: Optimal guard placement in polygonal galleries with holes
- **Convex decomposition**: Merge ears into convex components via shared edges
- **Visibility**: Which components each guard sees (polygon + hole boundaries only; bridges do not block sight)

## Implementation Philosophy

- Explicit orientation (Path) and segment intersection tests
- Point-in-polygon and segment containment built from ray casting and predicates
- No external geometry libraries (no shapely, CGAL, sympy)
- Correctness and clarity over performance

## Requirements

- Python ≥ 3.13

## Folder contents

| Type | Files |
|------|--------|
| **Core** | `art.py`, `box.py`, `convex.py`, `drawable.py`, `element.py`, `exceptions.py`, `guard.py`, `interval.py`, `matrix.py`, `model.py`, `path.py`, `point.py`, `polygon.py`, `segment.py`, `sequence.py`, `serializable.py`, `triangle.py`, `visibility.py` |
| **Examples** | `example1.py`, `example2.py`, `example3.py`, `example4.py`, `example5.py`, `example6.py`, `example7.py`, `example8.py`, `example9.py`, `example10.py` (and corresponding `exampleN.png` screenshots) |
| **Other** | `README.md`, `run.sh`, `.gitignore` |

## Modules

| Module | Contents |
|--------|----------|
| `art.py` | `ArtGallery` (Element2D, Drawable; holes, stitched boundary, ears, convex components, guards, post-process) |
| `box.py` | `Box`, `Bounded`; axis-aligned bounds and containment |
| `convex.py` | `ConvexComponent` (convex polygon, merge by shared edge, CCW) |
| `drawable.py` | `Drawable` (abstract: points, boundary, obstacles, ears, convex_components, guards, visibility; `PLOT_SIZE`, `plot()` for matplotlib figure) |
| `element.py` | `Element`, `ComplexElement`, `Element1D`, `Element2D` (contains, overlaps, size, signed_area) |
| `exceptions.py` | Art-gallery and geometry-specific exceptions |
| `guard.py` | `Guard`, `VertexGuard` (guard with `vertex` = position) |
| `interval.py` | `Interval` (1D), containment and overlap |
| `matrix.py` | `Matrix` (2×2 determinant for orientation/area) |
| `model.py` | `Model` (Hash id), `Hash`, `ModelMap[T]` (dict-like, `clone()`, add/pop) |
| `path.py` | `Path` (three points), `Orientation` (collinear/cw/ccw), signed area and orientation predicates |
| `point.py` | `Point`, `PointSequence` (vertices, signed area, CCW/CW, convexity, edges as `SegmentSequence`, unique, slice, append/insert/pop) |
| `polygon.py` | `Polygon` (simple, no duplicate points, non-zero area), edges as `SegmentSequence` |
| `segment.py` | `Segment`, `SegmentSequence`, `SegmentSet` (size, midpoint, connects, intersects, immutable set with `smallest`/`largest` that raise when empty) |
| `sequence.py` | Re-exports `PointSequence` from `point` |
| `serializable.py` | `Serializable` (abstract: `serialize()` → dict, `unserialize()` class method for API/JSON round-trip) |
| `triangle.py` | `Triangle`, `Ear` (convex ear for clipping), edges as `SegmentSequence` |
| `visibility.py` | `Visibility[T]` (guard → set of components or points, `sees`, `best`) |

## Art Gallery Pipeline

1. **Boundary**: CCW polygon; holes are CW. Validated on construction.
2. **Points**: Stitched boundary (polygon + holes connected by minimal bridges). Bridges avoid crossing edges and sliding along boundary.
3. **Ears**: Ear-clipping triangulation on the stitched polygon.
4. **Convex components**: Ears merged by shared edges into maximal convex polygons (`ModelMap[ConvexComponent]`).
5. **Guards**: Greedy visibility (pick guard that sees the most remaining components); then a post-process removes redundant guards by comparing each guard’s visible points to the union of the others’.
6. **Visibility**: Point-based visibility on the stitched boundary for the final guard set.

## Running

From the **project root** (not from `lab/`), use the npm scripts defined in `package.json`:

```bash
npm run test:lab:1
npm run test:lab:2
…
npm run test:lab:10
```

Or run all lab tests with `npm run test` (which runs `test:lab`, i.e. `test:lab:1`). Each script runs the corresponding `lab/exampleN.py`: it prints perimeter vertices, convex component count, guard count, and calls `gallery.plot()` to open a matplotlib window (save as `exampleN.png` to capture the figure). No need to import the drawable module; `ArtGallery` implements `Drawable` and provides `plot()`.

## Examples

| | |
|---|---|
| ![Example 1](example1.png) | ![Example 2](example2.png) |
| ![Example 3](example3.png) | ![Example 4](example4.png) |
| ![Example 5](example5.png) | ![Example 6](example6.png) |
| ![Example 7](example7.png) | ![Example 8](example8.png) |
| ![Example 9](example9.png) | ![Example 10](example10.png) |
