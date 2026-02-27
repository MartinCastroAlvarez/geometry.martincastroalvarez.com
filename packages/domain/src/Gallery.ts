/**
 * Gallery: published gallery with metadata and art-gallery geometry.
 *
 * Context: Wraps ArtGallery with id and optional title; used for list/detail from API.
 * id is required; title may be absent for unnamed galleries.
 *
 * Example:
 *   const g: Gallery = { id: 'g1', title: 'My gallery', artGallery: artGalleryInstance };
 */
import { ArtGallery } from './ArtGallery';

/** Published gallery with metadata (id, title) and geometry */
export interface Gallery {
    id: string;
    title?: string;
    artGallery: ArtGallery;
}
