import { ArtGallery } from './ArtGallery';

/** Published gallery with metadata (id, title) and geometry */
export interface Gallery {
    id: string;
    title?: string;
    artGallery: ArtGallery;
}
