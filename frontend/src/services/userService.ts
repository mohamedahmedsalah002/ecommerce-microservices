import { userApi, handleApiError } from './api';
import { 
  User, 
  UserLoginRequest, 
  UserRegisterRequest, 
  UserLoginResponse, 
  UserUpdateRequest,
  StandardResponse 
} from '../types';

export class UserService {
  // Register new user
  static async register(userData: UserRegisterRequest): Promise<StandardResponse<User>> {
    try {
      const response = await userApi.post('/api/v1/users/register', userData);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Login user
  static async login(credentials: UserLoginRequest): Promise<UserLoginResponse> {
    try {
      const response = await userApi.post('/api/v1/users/login', credentials);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Get user profile
  static async getProfile(): Promise<User> {
    try {
      const response = await userApi.get('/api/v1/users/profile');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Update user profile
  static async updateProfile(userData: UserUpdateRequest): Promise<StandardResponse<User>> {
    try {
      const response = await userApi.put('/api/v1/users/profile', userData);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Update password
  static async updatePassword(currentPassword: string, newPassword: string): Promise<StandardResponse> {
    try {
      const response = await userApi.patch('/api/v1/users/profile/password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Get user by ID (for admin or public profiles)
  static async getUserById(userId: string): Promise<User> {
    try {
      const response = await userApi.get(`/api/v1/users/profile/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

