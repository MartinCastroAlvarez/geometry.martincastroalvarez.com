import { ApiSolveRequest, ApiSolveResponse, ApiVerifyResponse } from './types'

// Hardcoded API URL as requested
const API_URL = 'https://geometry.api.martincastroalvarez.com'

export class ApiClient {
    private baseUrl: string

    constructor(baseUrl: string = API_URL) {
        this.baseUrl = baseUrl
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
