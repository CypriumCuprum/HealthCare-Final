import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/api';

// Create Auth Context
const AuthContext = createContext(null);

// In development, we'll use hardcoded tokens for testing
const TOKENS = {
  PATIENT: 'patient_token',
  DOCTOR: 'doctor_token',
  ADMIN: 'admin_token',
  PHARMACIST: 'admin_token', // Using admin token for pharmacist in this example
  DEFAULT: 'dev_token_123456'
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user');
    const storedRole = localStorage.getItem('user_role');
    
    if (token && storedUser) {
      setCurrentUser(JSON.parse(storedUser));
      setRole(storedRole);
    }
    
    setLoading(false);
  }, []);

  // Login function - in a real app, this would validate with the backend
  const login = async (username, password, selectedRole) => {
    setLoading(true);
    setError(null);
    
    try {
      // For development: Use hardcoded tokens based on role
      let token;
      
      // In a real app, we would call the login API
      // const response = await authService.login({ username, password });
      // token = response.data.access_token;
      
      // For development, simulate different user roles with hardcoded tokens
      switch(selectedRole) {
        case 'PATIENT':
          token = TOKENS.PATIENT;
          break;
        case 'DOCTOR':
          token = TOKENS.DOCTOR;
          break;
        case 'ADMIN':
          token = TOKENS.ADMIN;
          break;
        case 'PHARMACIST':
          token = TOKENS.PHARMACIST;
          break;
        default:
          token = TOKENS.DEFAULT;
      }
      
      // Create a mock user for development
      const user = {
        id: selectedRole === 'PATIENT' ? 1 : selectedRole === 'DOCTOR' ? 2 : 3,
        username,
        first_name: 'Test',
        last_name: 'User',
        email: `${username}@example.com`
      };
      
      // Save auth data to localStorage
      localStorage.setItem('auth_token', token);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('user_role', selectedRole);
      
      setCurrentUser(user);
      setRole(selectedRole);
      
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_role');
    setCurrentUser(null);
    setRole(null);
  };

  // Register function - normally would call the backend
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate successful registration
      // In a real app: const response = await authService.register(userData);
      
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
      return { success: false, error: err.message };
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
    loading,
    error,
    login,
    logout,
    register,
    hasRole,
    isAuthenticated: !!currentUser,
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