import { productApi, handleApiError } from './api';
import { 
  Product, 
  Category, 
  ProductListResponse, 
  ProductSearchParams,
  StandardResponse 
} from '../types';

export class ProductService {
  // Get all products with pagination
  static async getProducts(page: number = 1, perPage: number = 20): Promise<ProductListResponse> {
    try {
      const response = await productApi.get('/api/v1/products/', {
        params: { page, per_page: perPage }
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Search products with filters
  static async searchProducts(searchParams: ProductSearchParams): Promise<ProductListResponse> {
    try {
      const response = await productApi.get('/api/v1/products/search', {
        params: searchParams
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Get product by ID
  static async getProductById(productId: string): Promise<Product> {
    try {
      const response = await productApi.get(`/api/v1/products/${productId}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Get all categories
  static async getCategories(): Promise<Category[]> {
    try {
      const response = await productApi.get('/api/v1/categories/');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Get category by ID
  static async getCategoryById(categoryId: string): Promise<Category> {
    try {
      const response = await productApi.get(`/api/v1/categories/${categoryId}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Get products by category
  static async getProductsByCategory(categoryId: string, page: number = 1, perPage: number = 20): Promise<ProductListResponse> {
    try {
      const response = await productApi.get('/api/v1/products/search', {
        params: { 
          category_id: categoryId, 
          page, 
          per_page: perPage 
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Search products by query
  static async searchProductsByQuery(
    query: string, 
    page: number = 1, 
    perPage: number = 20
  ): Promise<ProductListResponse> {
    try {
      const response = await productApi.get('/api/v1/products/search', {
        params: { 
          query, 
          page, 
          per_page: perPage 
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Filter products by price range
  static async filterProductsByPrice(
    minPrice?: number, 
    maxPrice?: number, 
    page: number = 1, 
    perPage: number = 20
  ): Promise<ProductListResponse> {
    try {
      const response = await productApi.get('/api/v1/products/search', {
        params: { 
          min_price: minPrice,
          max_price: maxPrice,
          page, 
          per_page: perPage 
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

