import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
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
    }
})
