/**
 * App entry point: React root with providers.
 *
 * Context: Renders App inside ReactQueryProvider, BrowserRouter, LocaleProvider,
 * AnalyticsProvider, and AuthenticationProvider. Root element is #root; index.css
 * is imported for global and Tailwind styles.
 *
 * Example:
 *   ReactDOM.createRoot(document.getElementById('root')!).render(<App />);
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ReactQueryProvider, AuthenticationProvider } from '@geometry/data'
import { LocaleProvider } from '@geometry/i18n'
import { AnalyticsProvider } from '@geometry/analytics'
import { ThemeProvider } from '@geometry/theme'
import App from './App.tsx'
import './index.css'

const googleTagId = typeof import.meta.env.VITE_GOOGLE_TAG_ID === 'string' ? import.meta.env.VITE_GOOGLE_TAG_ID : null
// Only use test JWT from env in development; never in production (avoids leaking token from build or cookie).
const jwtToken =
  import.meta.env.DEV && typeof import.meta.env.VITE_JWT_TEST === 'string'
    ? import.meta.env.VITE_JWT_TEST
    : undefined

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ReactQueryProvider>
            <BrowserRouter future={{ v7_startTransition: true }}>
                <LocaleProvider>
                    <AnalyticsProvider googleTagId={googleTagId}>
                        <ThemeProvider>
                            <AuthenticationProvider jwtToken={jwtToken}>
                                <App />
                            </AuthenticationProvider>
                        </ThemeProvider>
                    </AnalyticsProvider>
                </LocaleProvider>
            </BrowserRouter>
        </ReactQueryProvider>
    </React.StrictMode>,
)
