import { Toaster as SonnerToaster, toast as sonnerToast } from 'sonner';

export const Toaster = () => (
    <SonnerToaster
        position="bottom-right"
        expand={true}
        richColors
        theme="system"
        className="toaster-wrapper"
    />
);

export const toast = sonnerToast;
