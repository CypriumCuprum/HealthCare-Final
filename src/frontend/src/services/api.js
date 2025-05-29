import axios from 'axios';

// Base URLs for our services - đảm bảo port đúng với cấu hình thực tế
const USER_SERVICE_URL = 'http://localhost:8000/api/v1';
const PHARMACY_SERVICE_URL = 'http://localhost:8001/api/v1';

// Create axios instances with default configs
const userServiceApi = axios.create({
  baseURL: USER_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const pharmacyServiceApi = axios.create({
  baseURL: PHARMACY_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token to all requests
const addAuthInterceptor = (axiosInstance) => {
  axiosInstance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
        console.log('Adding token to request:', {
          url: config.url,
          method: config.method,
          headers: config.headers
        });
      } else {
        console.log('No token found for request:', {
          url: config.url,
          method: config.method
        });
      }
      return config;
    },
    (error) => {
      console.error('Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  // Add response interceptor to handle errors
  axiosInstance.interceptors.response.use(
    (response) => {
      console.log('Response received:', {
        url: response.config.url,
        status: response.status,
        data: response.data
      });
      return response;
    },
    async (error) => {
      const originalRequest = error.config;
      
      // If error is 403 and we haven't tried to refresh token yet
      if (error.response?.status === 403 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          const refreshToken = localStorage.getItem('refresh_token');
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          console.log('Attempting to refresh token...');
          // Try to refresh the token
          const response = await userServiceApi.post('/token/refresh/', {
            refresh: refreshToken
          });

          const { access } = response.data;
          console.log('Token refreshed successfully');
          localStorage.setItem('auth_token', access);

          // Retry the original request with new token
          originalRequest.headers['Authorization'] = `Bearer ${access}`;
          return axiosInstance(originalRequest);
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          // Clear auth data and redirect to login
          localStorage.removeItem('auth_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          localStorage.removeItem('user_role');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      console.error('API Error:', {
        url: originalRequest.url,
        method: originalRequest.method,
        status: error.response?.status,
        data: error.response?.data,
        headers: originalRequest.headers
      });
      
      return Promise.reject(error);
    }
  );
};

// Apply the interceptor to both service instances
addAuthInterceptor(userServiceApi);
addAuthInterceptor(pharmacyServiceApi);

// Auth endpoints
export const authService = {
  login: (credentials) => userServiceApi.post('/login/', credentials),
  register: (userData) => userServiceApi.post('/register/', userData),
  getCurrentUser: () => userServiceApi.get('/users/me/'),
  verifyToken: (token) => userServiceApi.post('/token/verify/', { token }),
  refreshToken: (refresh) => userServiceApi.post('/token/refresh/', { refresh }),
};

// User endpoints
export const userService = {
  getUserDetails: (userId) => userServiceApi.get(`/users/${userId}/`),
  updateUserDetails: (userData) => userServiceApi.patch('/users/me/', userData),
  changePassword: (passwordData) => userServiceApi.post('/users/change_password/', passwordData),
};

// Medication catalog - available to all authenticated users
export const medicationService = {
  getMedications: () => pharmacyServiceApi.get('/medications/catalog/'),
  getMedicationById: (medicationId) => pharmacyServiceApi.get(`/medications/catalog/${medicationId}/`),
};

// Pharmacy endpoints - Doctor role
export const doctorPharmacyService = {
  createPrescription: (prescriptionData) => 
    pharmacyServiceApi.post('/prescriptions/', prescriptionData),
  getPatientPrescriptions: (patientId) => 
    pharmacyServiceApi.get(`/patients/${patientId}/prescriptions/`),
  getPrescriptionDetails: (prescriptionId) => 
    pharmacyServiceApi.get(`/prescriptions/${prescriptionId}/`),
};

// Pharmacy endpoints - Patient role
export const patientPharmacyService = {
  getMyPrescriptions: (patientId) => 
    pharmacyServiceApi.get(`/patients/${patientId}/prescriptions/`),
  getPrescriptionDetails: (prescriptionId) => 
    pharmacyServiceApi.get(`/prescriptions/${prescriptionId}/`),
};

// Pharmacy endpoints - Pharmacist role
export const pharmacistPharmacyService = {
  getPrescriptionDetails: (prescriptionId) => 
    pharmacyServiceApi.get(`/prescriptions/${prescriptionId}/`),
  getPendingPrescriptions: () => 
    pharmacyServiceApi.get('/pharmacy/prescriptions/pending/'),
  verifyPrescription: (prescriptionId) => 
    pharmacyServiceApi.post(`/pharmacy/prescriptions/${prescriptionId}/verify/`),
  dispenseMedication: (prescriptionId, dispenseData) => 
    pharmacyServiceApi.post(`/pharmacy/prescriptions/${prescriptionId}/dispense/`, dispenseData),
  getPharmacyStock: () => 
    pharmacyServiceApi.get('/pharmacy/stock/'),
  updateStock: (medicationId, stockData) => 
    pharmacyServiceApi.post(`/pharmacy/stock/${medicationId}/`, stockData),
};

// Admin endpoints
export const adminService = {
  // Medication catalog management
  createMedication: (medicationData) => 
    pharmacyServiceApi.post('/medications/catalog/', medicationData),
  updateMedication: (medicationId, medicationData) => 
    pharmacyServiceApi.put(`/medications/catalog/${medicationId}/`, medicationData),
  deleteMedication: (medicationId) => 
    pharmacyServiceApi.delete(`/medications/catalog/${medicationId}/`),
    
  // User management
  getUsers: () => 
    userServiceApi.get('/users/'),
  getUserById: (userId) => 
    userServiceApi.get(`/users/${userId}/`),
};

export default {
  authService,
  userService,
  medicationService,
  doctorPharmacyService,
  patientPharmacyService,
  pharmacistPharmacyService,
  adminService,
}; 