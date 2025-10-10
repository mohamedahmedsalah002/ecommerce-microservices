# E-commerce Frontend

A modern React TypeScript frontend application for the E-commerce platform, consuming User Service and Product Service APIs.

## Features

- ✅ **User Authentication** - Login, Register, Profile management
- ✅ **Product Catalog** - Browse, search, and filter products
- ✅ **Responsive Design** - Works on desktop and mobile devices
- ✅ **Modern UI** - Built with Tailwind CSS for beautiful styling
- ✅ **Type Safety** - Full TypeScript implementation
- ✅ **Protected Routes** - Authentication-based route protection
- ✅ **Error Handling** - Comprehensive error handling and user feedback
- ✅ **Loading States** - Smooth loading indicators
- ✅ **Search & Filter** - Advanced product search and filtering

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **React Router v6** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **Context API** - State management for authentication

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── LoadingSpinner.tsx
│   │   ├── Navbar.tsx
│   │   ├── ProductCard.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/           # React contexts
│   │   └── AuthContext.tsx
│   ├── pages/              # Page components
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Products.tsx
│   │   └── Profile.tsx
│   ├── services/           # API service layers
│   │   ├── api.ts
│   │   ├── userService.ts
│   │   └── productService.ts
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx            # Main app component
│   ├── App.css           # Global styles
│   ├── index.tsx         # App entry point
│   └── index.css         # Base styles
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## API Integration

### User Service (Port 8000)
- `POST /api/v1/users/register` - User registration
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile

### Product Service (Port 8001)
- `GET /api/v1/products/` - Get all products
- `GET /api/v1/products/search` - Search products with filters
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/categories/` - Get all categories

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- User Service running on port 8000
- Product Service running on port 8001

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm start
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000

### Build for Production

```bash
npm run build
```

## Features Overview

### Authentication
- **Registration**: Create new user accounts with validation
- **Login**: Secure JWT-based authentication
- **Profile Management**: Update user information
- **Protected Routes**: Authentication-required pages

### Product Catalog
- **Product Grid**: Responsive product display with images
- **Search**: Text search across product names and descriptions
- **Category Filter**: Filter products by category
- **Price Filter**: Filter by price range
- **Pagination**: Efficient navigation through large product lists

### UI/UX Features
- **Responsive Design**: Mobile-first approach
- **Loading States**: Smooth loading indicators
- **Error Handling**: User-friendly error messages
- **Form Validation**: Client-side form validation
- **Navigation**: Intuitive navigation with mobile menu

## Environment Configuration

The app connects to services running on:
- User Service: `http://localhost:8000`
- Product Service: `http://localhost:8001`

To change these URLs, modify the constants in `src/services/api.ts`:

```typescript
export const USER_SERVICE_URL = 'http://localhost:8000';
export const PRODUCT_SERVICE_URL = 'http://localhost:8001';
```

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code structure
2. Use TypeScript for all new components
3. Add proper error handling
4. Include loading states for async operations
5. Follow the established naming conventions

## Future Enhancements

- Shopping cart functionality
- Order management
- Payment integration
- Product reviews and ratings
- Wishlist functionality
- Admin panel for product management
- Real-time notifications
- Progressive Web App (PWA) features



