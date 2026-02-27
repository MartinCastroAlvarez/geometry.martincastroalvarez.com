/**
 * React Query provider and default options for the app.
 *
 * Context: Wraps the app so useQuery/useMutation (session, job, gallery) work.
 * Default staleTime comes from constants.ts (STALE_TIME_DEFAULT_MS). Per-query stale
 * times are defined in constants and used by session.ts, job.ts, gallery.ts.
 *
 * Example:
 *   <ReactQueryProvider>
 *     <App />
 *   </ReactQueryProvider>
 */

import { QueryClient, QueryClientProvider as TanStackQueryClientProvider } from '@tanstack/react-query'
import { ReactNode, useState } from 'react'
import { STALE_TIME_DEFAULT_MS } from './constants'

interface ReactQueryProviderProps {
    children: ReactNode
}

export const ReactQueryProvider = ({ children }: ReactQueryProviderProps) => {
    const [queryClient] = useState(() => new QueryClient({
        defaultOptions: {
            queries: {
                staleTime: STALE_TIME_DEFAULT_MS,
                refetchOnWindowFocus: false,
                retry: 1,
            },
        },
    }))

    return (
        <TanStackQueryClientProvider client={queryClient}>
            {children}
        </TanStackQueryClientProvider>
    )
};
