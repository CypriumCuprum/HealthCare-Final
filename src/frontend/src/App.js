import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import PatientDashboard from './pages/patient/Dashboard';
import DoctorDashboard from './pages/doctor/Dashboard';
import PharmacistDashboard from './pages/pharmacist/Dashboard';
import AdminDashboard from './pages/admin/Dashboard';

// Patient Pages
import PatientPrescriptions from './pages/patient/Prescriptions';
import PrescriptionDetails from './pages/patient/PrescriptionDetails';

// Doctor Pages
import CreatePrescription from './pages/doctor/CreatePrescription';
import DoctorPrescriptions from './pages/doctor/Prescriptions';

// Pharmacist Pages
import PendingPrescriptions from './pages/pharmacist/PendingPrescriptions';
import VerifyPrescription from './pages/pharmacist/VerifyPrescription';
import DispenseMedication from './pages/pharmacist/DispenseMedication';
import PharmacyStock from './pages/pharmacist/PharmacyStock';

// Admin Pages
import MedicationCatalog from './pages/admin/MedicationCatalog';

// Protected Route Component
const ProtectedRoute = ({ element, roles }) => {
  const { isAuthenticated, role, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (roles && !roles.includes(role)) {
    return <Navigate to="/" replace />;
  }
  
  return element;
};

// Main App
function AppContent() {
  const { isAuthenticated, role } = useAuth();
  
  return (
    <Router>
      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" replace />} />
        <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" replace />} />
        
        {/* Dashboard Route - redirects based on role */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute 
              element={
                role === 'PATIENT' ? <PatientDashboard /> :
                role === 'DOCTOR' ? <DoctorDashboard /> :
                role === 'PHARMACIST' ? <PharmacistDashboard /> :
                role === 'ADMIN' ? <AdminDashboard /> :
                <Navigate to="/login" replace />
              } 
              roles={['PATIENT', 'DOCTOR', 'PHARMACIST', 'ADMIN']} 
            />
          } 
        />
        
        {/* Patient Routes */}
        <Route 
          path="/patient/prescriptions" 
          element={<ProtectedRoute element={<PatientPrescriptions />} roles={['PATIENT']} />} 
        />
        <Route 
          path="/patient/prescriptions/:id" 
          element={<ProtectedRoute element={<PrescriptionDetails />} roles={['PATIENT']} />} 
        />
        
        {/* Doctor Routes */}
        <Route 
          path="/doctor/prescriptions/new" 
          element={<ProtectedRoute element={<CreatePrescription />} roles={['DOCTOR']} />} 
        />
        <Route 
          path="/doctor/prescriptions" 
          element={<ProtectedRoute element={<DoctorPrescriptions />} roles={['DOCTOR']} />} 
        />
        
        {/* Pharmacist Routes */}
        <Route 
          path="/pharmacist/prescriptions/pending" 
          element={<ProtectedRoute element={<PendingPrescriptions />} roles={['PHARMACIST']} />} 
        />
        <Route 
          path="/pharmacist/prescriptions/:id/verify" 
          element={<ProtectedRoute element={<VerifyPrescription />} roles={['PHARMACIST']} />} 
        />
        <Route 
          path="/pharmacist/prescriptions/:id/dispense" 
          element={<ProtectedRoute element={<DispenseMedication />} roles={['PHARMACIST']} />} 
        />
        <Route 
          path="/pharmacist/stock" 
          element={<ProtectedRoute element={<PharmacyStock />} roles={['PHARMACIST']} />} 
        />
        
        {/* Admin Routes */}
        <Route 
          path="/admin/medications" 
          element={<ProtectedRoute element={<MedicationCatalog />} roles={['ADMIN']} />} 
        />
        
        {/* Catch all - redirect to login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App; 