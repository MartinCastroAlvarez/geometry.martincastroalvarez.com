import { useContext } from 'react'
import { useStore } from 'zustand'
import { EditorContext } from './EditorContext'
import type { EditorStore } from './store'

export function useEditor<T>(selector: (state: EditorStore) => T): T {
    const store = useContext(EditorContext)
    if (!store) {
        throw new Error('useEditor must be used within EditorProvider')
    }
    return useStore(store, selector)
}
