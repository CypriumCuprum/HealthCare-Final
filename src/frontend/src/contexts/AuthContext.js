import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/api';

// Create Auth Context
const AuthContext = createContext(null);

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user');
    const storedRole = localStorage.getItem('user_role');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setCurrentUser(JSON.parse(storedUser));
      setRole(storedRole);
      
      // Verify token is still valid
      verifyToken(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  // Verify token validity with backend
  const verifyToken = async (token) => {
    try {
      console.log('Verifying token...');
      const response = await authService.verifyToken(token);
      console.log('Token verification response:', response.data);
      
      if (response.data.valid) {
        // Token is valid, update user state
        console.log('Token is valid');
        console.log('User data:', response.data);
        setCurrentUser({ id: response.data.user_id });
        setRole(response.data.role.name);
        setLoading(false);
      } else {
        // Token is invalid, logout
        console.log('Token is invalid, logout');
        logout();
      }
    } catch (err) {
      // Error verifying token, logout
      console.error('Token verification failed:', err);
      logout();
    }
  };

  // Login function
  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Attempting login...');
      // Call the real login API
      const response = await authService.login({ username, password });
      
      // Extract data from response
      const { access, refresh, user } = response.data;
      console.log('Login response:', {
        access: access ? `${access.substring(0, 10)}...` : null,
        refresh: refresh ? `${refresh.substring(0, 10)}...` : null,
        user: user
      });
      
      // Save auth data to localStorage
      localStorage.setItem('auth_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('user_role', user.role.name);
      
      console.log('Auth data saved to localStorage:', {
        auth_token: access ? `${access.substring(0, 10)}...` : null,
        refresh_token: refresh ? `${refresh.substring(0, 10)}...` : null,
        user: user,
        user_role: user.role.name
      });
      
      setToken(access);
      setCurrentUser(user);
      setRole(user.role.name);
      
      return { success: true };
    } catch (err) {
      console.error('Login error:', err);
      const errorMessage = err.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_role');
    setToken(null);
    setCurrentUser(null);
    setRole(null);
  };

  // Register function
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      await authService.register(userData);
      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Check if user has a specific role
  const hasRole = (requiredRole) => {
    return role === requiredRole;
  };

  // Context value
  const value = {
    currentUser,
    role,
    token,
    loading,
    error,
    login,
    logout,
    register,
    hasRole,
    isAuthenticated: !!currentUser && !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 