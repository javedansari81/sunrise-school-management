import axios from 'axios';

// Create axios instance for public gallery endpoints (no auth required)
const publicApi = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Gallery Types
export interface PublicGalleryImage {
  id: number;
  title: string;
  description?: string;
  cloudinary_url: string;
  cloudinary_thumbnail_url?: string;
  display_order: number;
  upload_date: string;
}

export interface PublicGalleryCategory {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  display_order: number;
  images: PublicGalleryImage[];
}

// Gallery API
export const galleryAPI = {
  // Get gallery images grouped by category (public endpoint)
  getPublicGalleryGrouped: (limitCategories?: number) =>
    publicApi.get<PublicGalleryCategory[]>('/public/gallery', {
      params: limitCategories ? { limit_categories: limitCategories } : undefined
    }),

  // Get all gallery categories (public endpoint)
  getCategories: (isActive?: boolean) =>
    publicApi.get('/gallery/categories', {
      params: isActive !== undefined ? { is_active: isActive } : undefined
    }),

  // Get images by category (public endpoint)
  getImagesByCategory: (categoryId: number) =>
    publicApi.get('/gallery/images', {
      params: { category_id: categoryId, is_active: true }
    }),

  // Get home page featured images (public endpoint)
  getHomePageImages: (limit: number = 10) =>
    publicApi.get<PublicGalleryImage[]>('/public/gallery/home-page', {
      params: { limit }
    }),
};

export default galleryAPI;

