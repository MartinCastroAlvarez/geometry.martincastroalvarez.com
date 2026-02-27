/**
 * Debounce hook: returns a stable function that invokes the callback after delay ms.
 *
 * Context: Each call clears the previous timeout and schedules a new one; only the last
 * invocation within the delay window runs. Callback and delay in deps; return type matches
 * the original function signature.
 *
 * Example:
 *   const debouncedSearch = useDebounce((q: string) => fetchSuggestions(q), 300);
 *   debouncedSearch(inputValue);
 */

import { useCallback, useRef } from "react";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const useDebounce = <T extends (...args: any[]) => any>(callback: T, delay: number): T => {
    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const debouncedCallback = useCallback(
        (...args: Parameters<T>) => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
            timeoutRef.current = setTimeout(() => {
                callback(...args);
            }, delay);
        },
        [callback, delay],
    ) as T;

    return debouncedCallback;
};
