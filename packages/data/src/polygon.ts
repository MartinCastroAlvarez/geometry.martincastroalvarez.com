/**
 * React Query hook for polygon validation (boundary and obstacles).
 *
 * Context: Accepts domain Polygon and Polygon[] from @geometry/domain; converts via
 * polygonToApiFormat (adapters) and calls GeometryApiClient.validatePolygon.
 * Validation is a public endpoint; token is optional. Returns validation result
 * dict (status and note keys). Used by the editor or job create flow to show
 * validation feedback before submitting.
 *
 * Example:
 *   const { mutateAsync: validatePolygon } = useValidatePolygon();
 *   const result = await validatePolygon({ boundary, obstacles });
 */

import { useMutation } from "@tanstack/react-query";
import type { Polygon } from "@geometry/domain";
import { GeometryApiClient } from "./geometry";
import { polygonToApiFormat } from "./adapters";
import { GEOMETRY_API_URL } from "./constants";
import type { PolygonValidationResponse } from "./types";
import { useAuthentication } from "./useAuthToken";

export interface ValidatePolygonParams {
    boundary: Polygon;
    obstacles: Polygon[];
}

export function useValidatePolygon() {
    const token = useAuthentication();
    const mutation = useMutation({
        mutationFn: async ({
            boundary,
            obstacles,
        }: ValidatePolygonParams): Promise<PolygonValidationResponse> => {
            const client = new GeometryApiClient(GEOMETRY_API_URL, token ?? undefined);
            const boundaryPoints = polygonToApiFormat(boundary);
            const obstaclesPoints = obstacles.map((obs) => polygonToApiFormat(obs));
            return client.validatePolygon(boundaryPoints, obstaclesPoints);
        },
    });
    return {
        ...mutation,
        validatePolygon: mutation.mutateAsync,
        isLoading: mutation.isPending,
    };
}
