import React, { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import { useSession, useLogout } from "@geometry/data";
import { HomePage, JobsPage, JobPage, GalleryPage, EditorPage } from "./pages";

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
    const { data: user, isLoading } = useSession();
    const logout = useLogout();
    useEffect(() => {
        if (!isLoading && !user) logout();
    }, [isLoading, user, logout]);
    if (isLoading || !user) return null;
    return <>{children}</>;
};

export const AppRoutes = () => (
    <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/jobs" element={<PrivateRoute><JobsPage /></PrivateRoute>} />
        <Route path="/jobs/:id" element={<PrivateRoute><JobPage /></PrivateRoute>} />
        <Route path="/editor" element={<PrivateRoute><EditorPage /></PrivateRoute>} />
        <Route path="/:id" element={<GalleryPage />} />
    </Routes>
);
