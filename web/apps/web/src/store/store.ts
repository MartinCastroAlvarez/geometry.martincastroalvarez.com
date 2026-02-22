import { createStore } from 'zustand/vanilla'
import { ArtGallery, Polygon, Point } from '@geometry/domain'
import { toast } from 'sonner'

export interface EditorState {
    gallery: ArtGallery
}

export interface EditorActions {
    setGallery: (gallery: ArtGallery) => void
    setPerimeter: (perimeter: Polygon) => void
    setHoles: (holes: Polygon[]) => void
    setGuards: (guards: Point[]) => void
    reset: () => void
}

export type EditorStore = EditorState & EditorActions

export const createEditorStore = (initState: Partial<EditorState> = {}) => {
    return createStore<EditorStore>()((set, get) => ({
        gallery: new ArtGallery(new Polygon([])),
        ...initState,


        setGallery: (gallery) => set({ gallery }),

        setPerimeter: (perimeter) => {
            const current = get().gallery
            // Basic validation: perimeter should be valid (e.g. simple polygon check if we had it)
            // For now, assume perimeter changes are mostly valid from UI, but we can prevent empty updates if needed
            if (!perimeter) return

            // TODO: check if existing holes are still inside new perimeter?
            // For now, we trust the UI/Logic to handle major conflicts or we let them exist temporarily
            set({ gallery: current.setPerimeter(perimeter) })
        },

        setHoles: (holes) => {
            if (!holes) return
            // Validate holes: check if they are inside perimeter, disjoint, etc.
            // Simplified check: just ensure they are mostly sane
            set((state) => ({
                gallery: new ArtGallery(state.gallery.perimeter, holes, state.gallery.guards)
            }))
        },

        setGuards: (guards) => {
            if (!guards) return
            set((state) => ({
                gallery: new ArtGallery(state.gallery.perimeter, state.gallery.holes, guards)
            }))
        },

        reset: () => {
            toast.info('Editor reset')
            set({
                gallery: new ArtGallery(new Polygon([]))
            })
        }
    }))
}
