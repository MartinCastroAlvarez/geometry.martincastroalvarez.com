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
            if (!perimeter) return
            set({ gallery: current.setPerimeter(perimeter) })
        },

        setHoles: (holes) => {
            if (!holes) return
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
