import { type ReactNode, useState } from 'react'
import { EditorContext } from './EditorContext'
import { createEditorStore } from './store'

export interface EditorProviderProps {
    children: ReactNode
}

export const EditorProvider = ({ children }: EditorProviderProps) => {
    const [store] = useState(() => createEditorStore())

    return (
        <EditorContext.Provider value={store}>
            {children}
        </EditorContext.Provider>
    )
}
