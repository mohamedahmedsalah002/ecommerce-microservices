// User types
export interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface UserRegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface UserLoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserUpdateRequest {
  name?: string;
  email?: string;
}

// Product types
export interface Category {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category_id: string | null;
  category_name: string | null;
  sku: string | null;
  stock_quantity: number;
  is_available: boolean;
  is_active: boolean;
  image_urls: string[];
  tags: string[];
  weight: number | null;
  dimensions: Record<string, number> | null;
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ProductSearchParams {
  query?: string;
  category_id?: string;
  min_price?: number;
  max_price?: number;
  tags?: string;
  is_available?: boolean;
  page?: number;
  per_page?: number;
}

// API Response types
export interface StandardResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

// Auth Context types
export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: UserUpdateRequest) => Promise<void>;
  isLoading: boolean;
}

// Cart types (for future use)
export interface CartItem {
  product: Product;
  quantity: number;
}

export interface Cart {
  items: CartItem[];
  total: number;
}

