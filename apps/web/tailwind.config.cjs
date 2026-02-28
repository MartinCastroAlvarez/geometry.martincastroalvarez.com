/**
 * Tailwind config (loaded from index.css via @config in v4).
 * In v4, only theme.extend (e.g. fontFamily, colors) is merged; safelist and content
 * are not supported here — use @source and @source inline() in index.css instead.
 * @type {import('tailwindcss').Config}
 */
module.exports = {
    theme: {
        extend: {
            fontFamily: {
                title: ["Oswald", "sans-serif"],
            },
            colors: {
                white: "#ffffff",
                primary: "rgba(255, 255, 255, 0.9)",
                muted: "rgba(255, 255, 255, 0.5)",
                neutral: "rgba(255, 255, 255, 0.5)",
                danger: "#fca5a5",
                success: "#86efac",
                dark: "#f1f5f9",
                none: "transparent",
                surface: "rgba(255, 255, 255, 0.1)",
                "surface-hover": "rgba(255, 255, 255, 0.1)",
                "surface-active": "rgba(255, 255, 255, 0.1)",
                "danger-bg": "rgba(239, 68, 68, 0.2)",
                "success-bg": "rgba(34, 197, 94, 0.2)",
                "dark-bg": "rgba(15, 23, 42, 0.6)",
                skeleton: "rgba(255, 255, 255, 0.5)",
                overlay: "rgba(0, 0, 0, 0.7)",
                focus: "rgba(251, 191, 36, 0.5)",
                ring: "#020617",
                slate: {
                    300: "rgba(255, 255, 255, 0.25)",
                },
            },
            borderColor: {
                muted: "rgba(255, 255, 255, 0.5)",
            },
            backgroundImage: {
                "primary-gradient":
                    "linear-gradient(to right, #a78bfa, #a855f7)",
                "body-gradient":
                    "linear-gradient(165deg, #0f172a 0%, #1e293b 35%, #1a1f2e 70%, #0f172a 100%)",
            },
        },
    },
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
        "../../packages/ui/src/**/*.{js,ts,jsx,tsx}",
    ],
    safelist: [
        "opacity-60",
        "rounded-full",
        "rounded-xl",
        "rounded-2xl",
        "rounded-lg",
        "rounded-md",
        "overflow-hidden",
        "overflow-visible",
        "overflow-y-auto",
        "overflow-x-hidden",
        "p-1",
        "p-2",
        "p-3",
        "p-4",
        "p-6",
        "px-2",
        "px-3",
        "px-4",
        "px-6",
        "py-1",
        "py-2",
        "py-3",
        "py-4",
        "m-2",
        "m-4",
        "gap-1",
        "gap-2",
        "gap-3",
        "gap-4",
        "gap-6",
        "border-2",
        "border-slate-400",
        "border-slate-300",
        "border-slate-200",
        "text-xs",
        "text-sm",
        "text-base",
        "text-lg",
        "flex",
        "flex-col",
        "flex-row",
        "items-center",
        "justify-center",
        "grid",
        "w-full",
    ],
};
