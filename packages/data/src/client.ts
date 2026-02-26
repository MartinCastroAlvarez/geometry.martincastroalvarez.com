import { ApiSolveRequest, ApiSolveResponse, ApiVerifyResponse } from './types'

const DEFAULT_API_URL = 'https://geometry.api.martincastroalvarez.com'

function getApiUrl(): string {
    let url: string | undefined
    try {
        const meta = import.meta as unknown as { env?: { VITE_GEOMETRY_API_URL?: string } }
        url = meta?.env?.VITE_GEOMETRY_API_URL
    } catch {
        url = undefined
    }
    if (!url && typeof process !== 'undefined' && process.env?.VITE_GEOMETRY_API_URL) {
        url = process.env.VITE_GEOMETRY_API_URL
    }
    if (url && url !== '' && url !== 'null' && url !== 'undefined') {
        return url
    }
    return DEFAULT_API_URL
}

export class ApiClient {
    private baseUrl: string

    constructor(baseUrl?: string) {
        this.baseUrl = baseUrl ?? getApiUrl()
    }

    async solveGuards(request: ApiSolveRequest): Promise<ApiSolveResponse> {
        const response = await fetch(`${this.baseUrl}/api/solve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        })

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`)
        }

        return response.json()
    }

    async verifyGuards(instanceId: string): Promise<ApiVerifyResponse> {
        const response = await fetch(`${this.baseUrl}/api/verify/${instanceId}`)

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`)
        }

        return response.json()
    }
}

export const apiClient = new ApiClient()
