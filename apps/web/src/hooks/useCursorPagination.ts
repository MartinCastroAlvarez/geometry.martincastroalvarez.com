/**
 * Token-trail pagination for list APIs: first page uses no token; forward appends
 * response next_token; backward reuses stored tokens without total count.
 */

import { useCallback, useReducer } from "react";

type State = { cursor: number; trail: (string | undefined)[] };

const initialState: State = { cursor: 0, trail: [undefined] };

type Action = { type: "next"; nextToken: string } | { type: "prev" } | { type: "reset" };

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "next": {
            if (!action.nextToken) return state;
            const { cursor, trail } = state;
            const nextCursor = cursor + 1;
            if (cursor === trail.length - 1) {
                return { cursor: nextCursor, trail: [...trail, action.nextToken] };
            }
            return { cursor: nextCursor, trail };
        }
        case "prev":
            return state.cursor > 0 ? { ...state, cursor: state.cursor - 1 } : state;
        case "reset":
            return initialState;
        default:
            return state;
    }
}

export function useCursorPagination() {
    const [state, dispatch] = useReducer(reducer, initialState);
    const requestNextToken = state.trail[state.cursor];

    const goNext = useCallback((nextToken: string) => {
        dispatch({ type: "next", nextToken });
    }, []);

    const goPrev = useCallback(() => {
        dispatch({ type: "prev" });
    }, []);

    const reset = useCallback(() => {
        dispatch({ type: "reset" });
    }, []);

    return {
        requestNextToken,
        pageIndex: state.cursor,
        canGoPrevious: state.cursor > 0,
        goNext,
        goPrev,
        reset,
    };
}
