/**
 * Domain package barrel: geometry and app entities.
 *
 * Context: Re-exports Point, User, Polygon, ArtGallery, Job, Gallery, ConvexComponent, Ear, Guard.
 * Used by packages/data and apps for API DTOs and UI models.
 *
 * Example:
 *   import { Point, User, ArtGallery } from '@repo/domain';
 *   const p = Point.fromDict({ x: 0, y: 0 });  const u = User.fromDict(dict);
 */
export * from './Point';
export * from './Status';
export * from './User';
export * from './Polygon';
export * from './ArtGallery';
export * from './Job';
export * from './Gallery';
export * from './ConvexComponent';
export * from './Ear';
export * from './Guard';
export * from './Summary';
export * from './Visibility';
