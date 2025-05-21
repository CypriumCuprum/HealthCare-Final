import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { doctorPharmacyService } from '../../services/api';

const DoctorDashboard = () => {
  const { currentUser } = useAuth();
  const [recentPrescriptions, setRecentPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Format date in a user-friendly way
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Add mock data for prescriptions since we don't have specific patient ID to fetch for
  useEffect(() => {
    // In a real app, this would fetch data from actual patients
    setLoading(true);
    
    // Simulate API call with timeout
    setTimeout(() => {
      // Mock data
      const mockPrescriptions = [
        {
          _id: 'presc1',
          patient_name: 'John Doe',
          patient_id: 1,
          doctor_name: `Dr. ${currentUser.first_name} ${currentUser.last_name}`,
          date_prescribed: new Date().toISOString(),
          status: 'PENDING_VERIFICATION',
          items: [
            { medication_name: 'Amoxicillin 500mg', dosage: '1 tablet', frequency: '3 times a day' }
          ]
        },
        {
          _id: 'presc2',
          patient_name: 'Jane Smith',
          patient_id: 2,
          doctor_name: `Dr. ${currentUser.first_name} ${currentUser.last_name}`,
          date_prescribed: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          status: 'VERIFIED',
          items: [
            { medication_name: 'Lisinopril 10mg', dosage: '1 tablet', frequency: 'daily' }
          ]
        },
        {
          _id: 'presc3',
          patient_name: 'Robert Johnson',
          patient_id: 3,
          doctor_name: `Dr. ${currentUser.first_name} ${currentUser.last_name}`,
          date_prescribed: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          status: 'DISPENSED_FULL',
          items: [
            { medication_name: 'Metformin 500mg', dosage: '1 tablet', frequency: 'twice daily' }
          ]
        }
      ];
      
      setRecentPrescriptions(mockPrescriptions);
      setLoading(false);
    }, 500);
  }, [currentUser]);

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

  return (
    <Layout>
      <div className="mb-4">
        <h2>Doctor Dashboard</h2>
        <p className="text-muted">Welcome, Dr. {currentUser.first_name}!</p>
      </div>

      <div className="dashboard-stats">
        <Card className="stat-card" bg="primary" text="white">
          <h3>{recentPrescriptions.length}</h3>
          <p>Recent Prescriptions</p>
        </Card>
        <Card className="stat-card" bg="info" text="white">
          <h3>0</h3>
          <p>Upcoming Appointments</p>
        </Card>
        <Card className="stat-card" bg="success" text="white">
          <h3>0</h3>
          <p>Patients Today</p>
        </Card>
      </div>

      <section className="mb-5">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h3 className="section-title">Recent Prescriptions</h3>
          <Link to="/doctor/prescriptions" className="btn btn-sm btn-outline-primary">
            View All
          </Link>
        </div>

        {loading ? (
          <p>Loading prescriptions...</p>
        ) : (
          <Row>
            {recentPrescriptions.map((prescription) => (
              <Col md={4} key={prescription._id} className="mb-3">
                <Card className="h-100">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <div>
                        <Card.Title>{prescription.patient_name}</Card.Title>
                        <Card.Subtitle className="mb-2 text-muted">
                          {formatDate(prescription.date_prescribed)}
                        </Card.Subtitle>
                      </div>
                      <Badge bg={getStatusBadgeVariant(prescription.status)}>
                        {prescription.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    
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
                      className="btn btn-sm btn-outline-secondary w-100"
                    >
                      View Details
                    </Link>
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </section>

      <section>
        <h3 className="section-title">Quick Actions</h3>
        <Row>
          <Col md={4}>
            <Card className="mb-3">
              <Card.Body>
                <Card.Title>Create New Prescription</Card.Title>
                <Card.Text>
                  Create a new prescription for a patient.
                </Card.Text>
                <Link to="/doctor/prescriptions/new" className="btn btn-primary">
                  New Prescription
                </Link>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="mb-3">
              <Card.Body>
                <Card.Title>View All Prescriptions</Card.Title>
                <Card.Text>
                  View all prescriptions you have created.
                </Card.Text>
                <Link to="/doctor/prescriptions" className="btn btn-outline-primary">
                  View Prescriptions
                </Link>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </section>
    </Layout>
  );
};

export default DoctorDashboard; 