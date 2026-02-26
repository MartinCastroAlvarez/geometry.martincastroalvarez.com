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
    instanceId: string
}

export type ApiVerifyResponse = {
    isValid: boolean
    coverage: number
}
