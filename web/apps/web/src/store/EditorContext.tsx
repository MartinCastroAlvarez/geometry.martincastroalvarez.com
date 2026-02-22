import { createContext } from 'react'
import type { StoreApi } from 'zustand'
import type { EditorStore } from './store'

export const EditorContext = createContext<StoreApi<EditorStore> | null>(null)
