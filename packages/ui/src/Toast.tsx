/**
 * Toast notifications: Toaster component and toast() API (via sonner).
 *
 * Context: Toaster renders Sonner at bottom-right, dark theme, expanded. toast() is the
 * sonner toast function (toast.success, toast.error, etc.). Mount Toaster once in app root.
 *
 * Example:
 *   // In root: <Toaster />
 *   toast.success('Saved');
 *   toast.error('Failed');
 */

import { Toaster as SonnerToaster, toast as sonnerToast } from 'sonner';

export const Toaster = () => (
    <SonnerToaster
        position="bottom-right"
        expand={true}
        richColors
        theme="dark"
        className="geometry-toaster toaster-wrapper"
    />
);

export const toast = sonnerToast;
