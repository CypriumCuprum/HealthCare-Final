import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Row, Col, Form } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { patientPharmacyService } from '../../services/api';

const PatientPrescriptions = () => {
  const { currentUser } = useAuth();
  const [prescriptions, setPrescriptions] = useState([]);
  const [filteredPrescriptions, setFilteredPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('ALL');

  // Fetch all prescriptions
  useEffect(() => {
    const fetchPrescriptions = async () => {
      try {
        const response = await patientPharmacyService.getMyPrescriptions(currentUser.id);
        const sortedPrescriptions = response.data.sort(
          (a, b) => new Date(b.date_prescribed) - new Date(a.date_prescribed)
        );
        setPrescriptions(sortedPrescriptions);
        setFilteredPrescriptions(sortedPrescriptions);
      } catch (err) {
        console.error('Error fetching prescriptions:', err);
        setError('Failed to load prescriptions');
        
        // For development, use mock data if API fails
        const mockPrescriptions = [
          {
            _id: 'presc1',
            patient_name: currentUser.first_name + ' ' + currentUser.last_name,
            doctor_name: 'Dr. Smith',
            date_prescribed: new Date().toISOString(),
            status: 'VERIFIED',
            items: [
              { medication_name: 'Amoxicillin 500mg', dosage: '1 tablet', frequency: '3 times a day' }
            ]
          },
          {
            _id: 'presc2',
            patient_name: currentUser.first_name + ' ' + currentUser.last_name,
            doctor_name: 'Dr. Johnson',
            date_prescribed: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'DISPENSED_FULL',
            items: [
              { medication_name: 'Ibuprofen 200mg', dosage: '1 tablet', frequency: 'as needed' }
            ]
          },
          {
            _id: 'presc3',
            patient_name: currentUser.first_name + ' ' + currentUser.last_name,
            doctor_name: 'Dr. Williams',
            date_prescribed: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'DISPENSED_FULL',
            items: [
              { medication_name: 'Lisinopril 10mg', dosage: '1 tablet', frequency: 'daily' },
              { medication_name: 'Hydrochlorothiazide 12.5mg', dosage: '1 tablet', frequency: 'daily' }
            ]
          },
          {
            _id: 'presc4',
            patient_name: currentUser.first_name + ' ' + currentUser.last_name,
            doctor_name: 'Dr. Brown',
            date_prescribed: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'PENDING_VERIFICATION',
            items: [
              { medication_name: 'Metformin 500mg', dosage: '1 tablet', frequency: 'twice daily' }
            ]
          }
        ];
        setPrescriptions(mockPrescriptions);
        setFilteredPrescriptions(mockPrescriptions);
      } finally {
        setLoading(false);
      }
    };

    fetchPrescriptions();
  }, [currentUser.id]);

  // Apply filter when filter changes
  useEffect(() => {
    if (filter === 'ALL') {
      setFilteredPrescriptions(prescriptions);
    } else {
      setFilteredPrescriptions(
        prescriptions.filter(prescription => prescription.status === filter)
      );
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
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <Layout>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>My Prescriptions</h2>
        <Form.Group>
          <Form.Select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            aria-label="Filter prescriptions"
          >
            <option value="ALL">All Prescriptions</option>
            <option value="PENDING_VERIFICATION">Pending Verification</option>
            <option value="VERIFIED">Verified</option>
            <option value="DISPENSED_PARTIAL">Partially Dispensed</option>
            <option value="DISPENSED_FULL">Fully Dispensed</option>
            <option value="CANCELLED">Cancelled</option>
          </Form.Select>
        </Form.Group>
      </div>

      {loading ? (
        <p>Loading prescriptions...</p>
      ) : error ? (
        <Card className="p-3">
          <p className="text-danger mb-0">{error}</p>
        </Card>
      ) : filteredPrescriptions.length === 0 ? (
        <Card className="p-4">
          <Card.Body className="text-center">
            <h5>No prescriptions found</h5>
            <p className="text-muted">
              {filter === 'ALL' 
                ? "You don't have any prescriptions yet." 
                : `You don't have any prescriptions with status "${filter.replace('_', ' ')}".`}
            </p>
          </Card.Body>
        </Card>
      ) : (
        <Row>
          {filteredPrescriptions.map((prescription) => (
            <Col md={6} lg={4} className="mb-4" key={prescription._id}>
              <Card className="h-100">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <Card.Title>Prescription</Card.Title>
                      <Card.Subtitle className="mb-2 text-muted">
                        {formatDate(prescription.date_prescribed)}
                      </Card.Subtitle>
                    </div>
                    <Badge bg={getStatusBadgeVariant(prescription.status)}>
                      {prescription.status.replace(/_/g, ' ')}
                    </Badge>
                  </div>
                  
                  <p className="mb-2"><strong>Doctor:</strong> {prescription.doctor_name}</p>
                  
                  <div className="mt-3">
                    <p className="mb-1"><strong>Medications:</strong></p>
                    <ul className="ps-3">
                      {prescription.items.map((item, index) => (
                        <li key={index}>
                          {item.medication_name} - {item.dosage}, {item.frequency}
                        </li>
                      ))}
                    </ul>
                  </div>
                </Card.Body>
                <Card.Footer className="bg-white">
                  <Link 
                    to={`/patient/prescriptions/${prescription._id}`} 
                    className="btn btn-primary w-100"
                  >
                    View Details
                  </Link>
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Layout>
  );
};

export default PatientPrescriptions; 