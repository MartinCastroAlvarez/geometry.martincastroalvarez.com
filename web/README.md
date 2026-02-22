# Geometry Art Gallery - Web Application

Editor visual interactivo para experimentar con el **Art Gallery Problem**.

## Getting Started

### Prerequisites
- Node.js >= 18.0.0
- pnpm >= 9.0.0

### Installation

```bash
# Desde la raíz del monorepo
cd web
pnpm install
```

### Running the App

```bash
# Levantar el servidor de desarrollo (apps/web)
pnpm dev:web
```

Esto iniciará Vite en `http://localhost:5173`

### Other Commands

```bash
# Build de producción
pnpm build

# Linter
pnpm lint

# Type checking
pnpm typecheck

# Limpiar node_modules
pnpm clean
```

## Tech Stack

### Rendering & Interaction
- **React Konva**: Canvas-based polygon editor con soporte para arrastre de vértices, agujeros y overlays de visibilidad
- **@use-gesture/react**: Gestures naturales (drag, pinch, wheel)
- **d3-zoom**: Pan/Zoom suave y controlable

### Geometry Processing
- **polygon-clipping**: Operaciones booleanas (unión, diferencia, intersección) para gestionar agujeros
- **martinez**: Algoritmo Martinez-Rueda para polígonos complejos
- **earcut**: Triangulación rápida para rendering optimizado
- **rbush**: Índice espacial para detección eficiente de vértices/aristas

### Rendering & Styling
*   **Rendering:** React Konva (Canvas).
*   **Styling:** Tailwind CSS (Utility-first) + CSS Variables (Theme System).
*   **Gestión de Datos:** React Query.

### App Composition
La aplicación principal- **apps/**
  - **web**: Main React application (Vite).
  - **mobile**: React Native application (Expo).
- **packages/**
  - **ui**: Shared UI components (React + Tailwind).
  - **core**: Core domain logic and algorithms.
  - **data**: API client and React Query provider.
  - **editor**: Editor logic and components.
e central que recibe una instancia de `ArtGallery` (Outer Polygon + Holes + Guards). Gestiona la interacción directa (drag & drop de huecos, dibujo) y emite eventos `onChange`.

## Project Structure

```
web/
├── apps/
│   ├── web/              # Aplicación web principal (Vite + React)
│   └── mobile/           # Placeholder para Expo React Native
├── packages/
│   ├── ui/               # Componentes visuales compartidos
│   │   ├── Container     # Layout básico (Grid/Flex)
│   │   ├── Text/Title    # Tipografía estandarizada
│   │   └── Button        # Botones interactivos y acciones
│   ├── data/             # React Query
│   ├── domain/           # Tipos de geometría + utils puros
│   │   ├── Modelos: Point, Polygon, ArtGallery
│   │   └── Lógica: toDict(), validaciones invariantes
│   └── config/           # Configs compartidas (eslint, tsconfig)
├── pnpm-workspace.yaml
├── package.json
└── turbo.json
```

## Features

- ✅ Editor de polígonos con drag & drop
- ✅ Soporte para agujeros (holes)
- ✅ Colocación interactiva de guardias
- ✅ Visualización de regiones visibles por guardia
- ✅ Integración con backend de algoritmos de aproximación
- ✅ Modo step-by-step para ver decisiones del algoritmo
- ✅ Export/Import de instancias (GeoJSON-like)

## Environment Variables

Crear un archivo `.env.local` en `apps/web/`:

```env
VITE_API_URL=http://localhost:8000
```

## Development Workflow

1. Hacer cambios en `apps/web/src/` o en los packages
2. Hot reload automático en el navegador
3. Los cambios en packages se reflejan inmediatamente gracias a los workspace links de pnpm
