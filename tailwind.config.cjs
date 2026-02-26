/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./apps/web/index.html",
        "./apps/web/src/**/*.{js,ts,jsx,tsx}",
        "./packages/ui/src/**/*.{js,ts,jsx,tsx}",
    ],
    safelist: [
        "rounded-full",
        "rounded-xl",
        "rounded-lg",
        "overflow-hidden",
        "p-4",
        "gap-2",
    ],
    theme: {
        extend: {
            colors: {
                "x-surface": "rgba(255, 250, 245, 0.12)",
                "x-surface-strong": "rgba(255, 250, 245, 0.18)",
                "x-text": "#f5f0e8",
                "x-text-muted": "#c4b8a8",
                "x-dark": "#a89888",
                "x-white": "#faf8f5",
                "x-gray": "rgba(255, 250, 245, 0.15)",
                "x-border": "rgba(255, 250, 245, 0.08)",
                "x-border-subtle": "rgba(255, 250, 245, 0.04)",
            },
        },
    },
};
