import React from 'react'
import ReactDOM from 'react-dom/client'
import { ReactQueryProvider } from '@geometry/data'
import { EditorProvider } from './store'
import App from './App.tsx'
import '../../../packages/ui/src/Theme.css'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ReactQueryProvider>
            <EditorProvider>
                <App />
            </EditorProvider>
        </ReactQueryProvider>
    </React.StrictMode>,
)
