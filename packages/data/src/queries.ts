import { useMutation } from '@tanstack/react-query'
import { ArtGallery } from '@geometry/domain'
import { apiClient } from './client'
import { domainToApi } from './adapters'
import { ApiSolveResponse } from './types'

export const useSolveGallery = () => {
    return useMutation<ApiSolveResponse, Error, ArtGallery>({
        mutationFn: (gallery: ArtGallery) => {
            const apiRequest = domainToApi(gallery)
            return apiClient.solveGuards(apiRequest)
        }
    })
}
