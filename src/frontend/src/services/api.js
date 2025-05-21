import axios from 'axios';

// Base URLs for our services
const USER_SERVICE_URL = 'http://localhost:8000/api/v1';
const PHARMACY_SERVICE_URL = 'http://localhost:8081/api/v1';

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
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
};

// Apply the interceptor to our instances
addAuthInterceptor(userServiceApi);
// addAuthInterceptor(pharmacyServiceApi);

// Auth endpoints
export const authService = {
  login: (credentials) => userServiceApi.post('/users/login/', credentials),
  register: (userData) => userServiceApi.post('/users/register/', userData),
  getCurrentUser: () => userServiceApi.get('/users/me/'),
  verifyToken: (token) => userServiceApi.post('/users/token/verify/', { token }),
};

// User endpoints
export const userService = {
  getUserDetails: (userId) => userServiceApi.get(`/users/${userId}/`),
  updateUserDetails: (userData) => userServiceApi.put('/users/me/', userData),
  changePassword: (passwordData) => userServiceApi.post('/users/password/change/', passwordData),
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
  getMedications: () => 
    pharmacyServiceApi.get('/admin/medications/catalog/'),
  getMedicationById: (medicationId) => 
    pharmacyServiceApi.get(`/admin/medications/catalog/${medicationId}/`),
  createMedication: (medicationData) => 
    pharmacyServiceApi.post('/admin/medications/catalog/', medicationData),
  updateMedication: (medicationId, medicationData) => 
    pharmacyServiceApi.put(`/admin/medications/catalog/${medicationId}/`, medicationData),
  deleteMedication: (medicationId) => 
    pharmacyServiceApi.delete(`/admin/medications/catalog/${medicationId}/`),
    
  // User management (for future implementation)
  getUsers: () => 
    userServiceApi.get('/admin/users/'),
  getUserById: (userId) => 
    userServiceApi.get(`/admin/users/${userId}/`),
};

export default {
  authService,
  userService,
  doctorPharmacyService,
  patientPharmacyService,
  pharmacistPharmacyService,
  adminService,
}; 