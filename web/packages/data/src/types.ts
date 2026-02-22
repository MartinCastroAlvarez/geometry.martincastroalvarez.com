// API Data Types (not interfaces, as requested)

export type ApiPoint = {
    x: number
    y: number
}

export type ApiPolygon = {
    points: ApiPoint[]
}

export type ApiSolveRequest = {
    perimeter: ApiPolygon
    holes: ApiPolygon[]
}

export type ApiSolveResponse = {
    jobId: string
}

export type ApiVerifyRequest = {
    instanceId: string // Used in URL mostly, but defining type for consistency if needed
}

export type ApiVerifyResponse = {
    isValid: boolean
    coverage: number // 0 to 1
}
