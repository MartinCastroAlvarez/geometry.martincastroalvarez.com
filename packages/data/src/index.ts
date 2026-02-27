/**
 * Public API of the @geometry/data package.
 *
 * Context: Re-exports constants, auth/cookies, API clients (auth, geometry), types,
 * adapters, React Query hooks (session, job, gallery), and the ReactQueryProvider.
 * Apps should import from "@geometry/data" or "@geom/data" (alias), not from internal paths.
 *
 * Example:
 *   import { useSession, useJobs, useArtGallery, fetchWithAuth } from "@geometry/data";
 */

export * from "./constants";
export * from "./cookies";
export * from "./auth";
export * from "./geometry";
export * from "./types";
export * from "./adapters";
export * from "./session";
export * from "./job";
export * from "./gallery";
export * from "./ReactQueryProvider";
