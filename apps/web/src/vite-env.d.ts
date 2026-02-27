/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_GOOGLE_TAG_ID?: string
    readonly VITE_JWT_TEST?: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}
