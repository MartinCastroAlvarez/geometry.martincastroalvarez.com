/** @type {import('tailwindcss').Config} */
module.exports = {
    theme: {
        extend: {
            fontFamily: {
                title: ["Oswald", "sans-serif"],
            },
        },
    },
    content: [
        "./apps/web/index.html",
        "./apps/web/src/**/*.{js,ts,jsx,tsx}",
        "./packages/ui/src/**/*.{js,ts,jsx,tsx}",
    ],
    safelist: [
        "rounded-full",
        "rounded-xl",
        "rounded-2xl",
        "rounded-lg",
        "overflow-hidden",
        "p-4",
        "gap-2",
        "gap-3",
        "gap-4",
        "gap-6",
        "border-2",
        "border-slate-400",
        "border-slate-300",
        "border-slate-200",
    ],
};
