import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { execSync } from 'node:child_process'

const getJwtTest = (): string => {
    if (process.env.VITE_JWT_TEST) return process.env.VITE_JWT_TEST
    try {
        const spyPath = path.resolve(__dirname, '../../spy.sh')
        return execSync(`bash "${spyPath}" martin com.martincastroalvarez.secrets JWT_TEST`, {
            encoding: 'utf8',
            cwd: path.resolve(__dirname, '../..'),
        }).trim()
    } catch {
        return ''
    }
};

export default defineConfig({
    define: {
        'import.meta.env.VITE_JWT_TEST': JSON.stringify(getJwtTest()),
    },
    plugins: [react()],
    resolve: {
        alias: {
            '@geom/ui': path.resolve(__dirname, '../../packages/ui/src'),
            '@geom/data': path.resolve(__dirname, '../../packages/data/src'),
            '@geom/domain': path.resolve(__dirname, '../../packages/domain/src'),
        }
    },
    server: {
        port: 5174,
        host: true
    },
})
