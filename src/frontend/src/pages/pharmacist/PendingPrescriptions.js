import React, { useState, useEffect } from 'react';
import { Card, Badge, Table, Button, Form } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { pharmacistPharmacyService } from '../../services/api';

const PendingPrescriptions = () => {
  const { currentUser } = useAuth();
  const [prescriptions, setPrescriptions] = useState([]);
  const [filteredPrescriptions, setFilteredPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('PENDING_VERIFICATION');

  // Fetch prescriptions from API
  useEffect(() => {
    const fetchPrescriptions = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await pharmacistPharmacyService.getPendingPrescriptions();
        setPrescriptions(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching prescriptions:', err);
        setError('Failed to load prescriptions. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchPrescriptions();
  }, []);

  // Apply filters when they change
  useEffect(() => {
    if (prescriptions.length > 0) {
      let filtered = [...prescriptions];
      
      // Apply status filter
      if (filter !== 'ALL') {
        filtered = filtered.filter(p => p.status === filter);
      }
      
      // Sort by date (oldest pending first)
      filtered.sort((a, b) => new Date(a.date_prescribed) - new Date(b.date_prescribed));
      
      setFilteredPrescriptions(filtered);
    }
  }, [filter, prescriptions]);

  // Helper function to get appropriate badge color based on prescription status
  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'PENDING_VERIFICATION':
        return 'warning';
      case 'VERIFIED':
        return 'info';
      case 'DISPENSED_PARTIAL':
        return 'primary';
      case 'DISPENSED_FULL':
        return 'success';
      case 'CANCELLED':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  // Format date in a user-friendly way
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <Layout>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Pending Prescriptions</h2>
      </div>

      <Card className="mb-4">
        <Card.Body>
          <Card.Title>Filters</Card.Title>
          <Form.Group className="mb-3">
            <Form.Label>Status</Form.Label>
            <Form.Select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="PENDING_VERIFICATION">Pending Verification</option>
              <option value="VERIFIED">Verified</option>
              <option value="DISPENSED_PARTIAL">Partially Dispensed</option>
              <option value="DISPENSED_FULL">Fully Dispensed</option>
              <option value="CANCELLED">Cancelled</option>
            </Form.Select>
          </Form.Group>
        </Card.Body>
      </Card>

      {loading ? (
        <p>Loading prescriptions...</p>
      ) : error ? (
        <p className="text-danger">{error}</p>
      ) : filteredPrescriptions.length === 0 ? (
        <Card className="p-4">
          <Card.Body className="text-center">
            <h5>No prescriptions found</h5>
            <p className="text-muted">
              Try adjusting your filters or check back later.
            </p>
          </Card.Body>
        </Card>
      ) : (
        <Table responsive hover>
          <thead>
            <tr>
              <th>Date</th>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Medications</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredPrescriptions.map(prescription => (
              <tr key={prescription._id}>
                <td>{formatDate(prescription.date_prescribed)}</td>
                <td>{prescription.patient_name}</td>
                <td>{prescription.doctor_name}</td>
                <td>
                  <ul className="m-0 ps-3">
                    {prescription.items.map((item, index) => (
                      <li key={index}>{item.medication_name}</li>
                    ))}
                  </ul>
                </td>
                <td>
                  <Badge bg={getStatusBadgeVariant(prescription.status)}>
                    {prescription.status.replace(/_/g, ' ')}
                  </Badge>
                </td>
                <td>
                  {prescription.status === 'PENDING_VERIFICATION' && (
                    <Link 
                      to={`/pharmacist/prescriptions/${prescription._id}/verify`} 
                      className="btn btn-sm btn-primary me-2"
                    >
                      Verify
                    </Link>
                  )}
                  {prescription.status === 'VERIFIED' && (
                    <Link 
                      to={`/pharmacist/prescriptions/${prescription._id}/dispense`} 
                      className="btn btn-sm btn-success me-2"
                    >
                      Dispense
                    </Link>
                  )}
                  <Link 
                    to={`/patient/prescriptions/${prescription._id}`} 
                    className="btn btn-sm btn-outline-secondary"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Layout>
  );
};

export default PendingPrescriptions; 