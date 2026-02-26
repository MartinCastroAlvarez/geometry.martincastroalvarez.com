import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ReactQueryProvider } from '@geometry/data'
import { LocaleProvider } from '@geometry/i18n'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ReactQueryProvider>
            <BrowserRouter>
                <LocaleProvider>
                    <App />
                </LocaleProvider>
            </BrowserRouter>
        </ReactQueryProvider>
    </React.StrictMode>,
)
