/**
 * Auth token context: React context for the JWT used by API clients.
 *
 * Context: Holds the optional JWT (string | null) that the app passes via AuthenticationProvider.
 * AuthenticationProvider (AuthenticationProvider.tsx) supplies the value and syncs it to the data
 * from prop or cookie; useAuthToken / useAuthentication (useAuthToken.ts) consume it. The
 * context is created here and left undefined until a provider mounts. Do not put provider or
 * hook logic in this file.
 *
 * Example:
 *   import { AuthTokenContext } from "./AuthenticationContext";
 *   const token = useContext(AuthTokenContext);  // prefer useAuthToken() instead
 */

import React, { createContext } from "react";

export const AuthTokenContext = createContext<string | null | undefined>(undefined);
