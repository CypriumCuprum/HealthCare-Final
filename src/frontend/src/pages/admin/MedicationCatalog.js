import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Alert, Spinner } from 'react-bootstrap';
import { medicationService, adminService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const MedicationCatalog = () => {
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { hasRole, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  const isAdmin = hasRole('ADMIN');
  
  useEffect(() => {
    if (!isAuthenticated) {
      console.log('Not authenticated, redirect to login');
      navigate('/login');
      return;
    }
    fetchMedications();
  }, [isAuthenticated, navigate]);
  
  const fetchMedications = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching medications');
      // Get medication catalog from API
      const response = await medicationService.getMedications();
      setMedications(response.data);
    } catch (err) {
      console.error('Error fetching medications:', err);
      setError(err.response?.data?.detail || 'Failed to load medications. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this medication?')) {
      return;
    }
    
    try {
      await adminService.deleteMedication(id);
      // Update the medications list
      fetchMedications();
    } catch (err) {
      console.error('Error deleting medication:', err);
      setError('Failed to delete medication. Please try again.');
    }
  };
  
  if (loading) {
    return (
      <Container className="d-flex justify-content-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }
  
  return (
    <Container className="my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Medication Catalog</h2>
        {isAdmin && (
          <Button variant="primary" href="/admin/medications/new">
            Add New Medication
          </Button>
        )}
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {medications.length === 0 ? (
        <p>No medications found.</p>
      ) : (
        <Table responsive striped bordered hover>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Description</th>
              <th>Dosage</th>
              <th>Unit Price</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {medications.map((medication) => (
              <tr key={medication.id}>
                <td>{medication.id}</td>
                <td>{medication.name}</td>
                <td>{medication.description}</td>
                <td>{medication.dosage_form}</td>
                <td>${medication.unit_price}</td>
                {isAdmin && (
                  <td>
                    <Button 
                      variant="outline-primary" 
                      size="sm" 
                      className="me-2"
                      href={`/admin/medications/${medication.id}`}
                    >
                      Edit
                    </Button>
                    <Button 
                      variant="outline-danger" 
                      size="sm"
                      onClick={() => handleDelete(medication.id)}
                    >
                      Delete
                    </Button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
};

export default MedicationCatalog; 