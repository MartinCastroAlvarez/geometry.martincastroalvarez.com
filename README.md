# geometry.martincastroalvarez.com

Computational geometry project: art gallery algorithms, convex decomposition, and guard placement from first principles.

## Documentation by area

| Area | Description | Readme |
|------|-------------|--------|
| **Lab** | Python prototype, examples, and art gallery pipeline | [lab/README.md](lab/README.md) |
| **API** | REST and worker backend (Lambda, S3, SQS, repositories, indexes) | [api/README.md](api/README.md) |

## Lab examples

The [lab](lab/) directory contains a Python prototype and example galleries. Each example builds an art gallery (polygon with holes), runs the pipeline (stitched boundary, ear-clipping triangulation, convex components, guards), and can be visualized (save the figure as `exampleN.png`).

| | |
|---|---|
| ![Example 1](lab/example1.png) | ![Example 2](lab/example2.png) |
| ![Example 3](lab/example3.png) | ![Example 4](lab/example4.png) |
| ![Example 5](lab/example5.png) | ![Example 6](lab/example6.png) |
| ![Example 7](lab/example7.png) | ![Example 8](lab/example8.png) |
| ![Example 9](lab/example9.png) | ![Example 10](lab/example10.png) |

## Build, deploy, and test

Use **Node.js 25** for npm and CDK (e.g. run `nvm use 25` if using nvm).

From the project root:

- **Install and bootstrap:** `npm run init` (uses AWS profile `martin`; run `npm run update` to only install dependencies).
- **Build:** `npm run build` (runs `build:api` and `build:cdk`). Use `npm run build:api` or `npm run build:cdk` for specific parts.
- **Deploy:** `npm run deploy` (update, build, CDK deploy, then CloudFront invalidation via `npm run publish`).
- **Publish (invalidation only):** `npm run publish` (invalidates the geometry CloudFront distribution using `GeometryStack` / `GeometryDistributionId` from `outputs.json`).
- **Test:** `npm run test` (runs `test:lab`). Use `npm run test:lab:1` … `npm run test:lab:10` to run `lab/example1.py` … `lab/example10.py`.
