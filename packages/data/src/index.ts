/**
 * Public API of the @geometry/data package.
 *
 * Context: Re-exports constants, auth/cookies, API clients (auth, geometry), types,
 * adapters, React Query hooks (session, job, gallery), and the ReactQueryProvider.
 * Apps should import from "@geometry/data" or "@geom/data" (alias), not from internal paths.
 *
 * Example:
 *   import { useSession, useJobs, useArtGallery, useAuthentication } from "@geometry/data";
 *   const { user } = useSession(); const { jobs } = useJobs(); const { gallery } = useArtGallery(id);
 */

export * from "./constants";
export { getAuthToken } from "./cookies";
export { AuthTokenContext } from "./AuthenticationContext";
export { AuthenticationProvider } from "./AuthenticationProvider";
export type { AuthenticationProviderProps } from "./AuthenticationProvider";
export { useAuthToken, useAuthentication } from "./useAuthToken";
export * from "./auth";
export * from "./geometry";
export * from "./types";
export * from "./adapters";
export * from "./session";
export * from "./job";
export * from "./gallery";
export * from "./polygon";
export * from "./ReactQueryProvider";
