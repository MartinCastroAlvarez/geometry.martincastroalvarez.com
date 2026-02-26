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
        "overflow-hidden",
        "p-4",
        "gap-2",
    ],
    theme: {
        extend: {
            colors: {
                dark: "#1a1a1a",
                "x-white": "#ffffff",
                "x-gray": "#e0e0e0",
                "x-dark": "rgba(55, 65, 81, 1)",
                primary: "#0f62fe",
            },
        },
    },
    plugins: [],
}
