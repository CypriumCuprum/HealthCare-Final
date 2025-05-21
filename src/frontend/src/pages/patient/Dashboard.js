import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { patientPharmacyService } from '../../services/api';

const PatientDashboard = () => {
  const { currentUser } = useAuth();
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch recent prescriptions
  useEffect(() => {
    const fetchRecentPrescriptions = async () => {
      try {
        const response = await patientPharmacyService.getMyPrescriptions(currentUser.id);
        // Sort by date and take the most recent 3
        const sortedPrescriptions = response.data
          .sort((a, b) => new Date(b.date_prescribed) - new Date(a.date_prescribed))
          .slice(0, 3);
        setPrescriptions(sortedPrescriptions);
      } catch (err) {
        console.error('Error fetching prescriptions:', err);
        setError('Failed to load prescriptions');
        
        // For development, use mock data if API fails
        setPrescriptions([
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
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentPrescriptions();
  }, [currentUser.id]);

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
      <div className="mb-4">
        <h2>Welcome, {currentUser.first_name}!</h2>
        <p className="text-muted">Here's an overview of your healthcare information</p>
      </div>

      <div className="dashboard-stats">
        <Card className="stat-card">
          <h3>{prescriptions.length}</h3>
          <p>Recent Prescriptions</p>
        </Card>
        <Card className="stat-card">
          <h3>0</h3>
          <p>Upcoming Appointments</p>
        </Card>
        <Card className="stat-card">
          <h3>0</h3>
          <p>Pending Lab Results</p>
        </Card>
      </div>

      <section className="mb-5">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h3 className="section-title">Recent Prescriptions</h3>
          <Link to="/patient/prescriptions" className="btn btn-sm btn-outline-primary">
            View All
          </Link>
        </div>

        {loading ? (
          <p>Loading prescriptions...</p>
        ) : error ? (
          <Card className="p-3">
            <p className="text-danger mb-0">{error}</p>
          </Card>
        ) : prescriptions.length === 0 ? (
          <Card className="p-3">
            <p className="mb-0">You don't have any prescriptions yet.</p>
          </Card>
        ) : (
          <Row>
            {prescriptions.map((prescription) => (
              <Col md={4} key={prescription._id}>
                <Card className="prescription-card">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <Card.Title className="mb-0">Prescription</Card.Title>
                      <Badge bg={getStatusBadgeVariant(prescription.status)}>
                        {prescription.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    <Card.Subtitle className="mb-2 text-muted">
                      {formatDate(prescription.date_prescribed)}
                    </Card.Subtitle>
                    
                    <p className="mb-1"><strong>Doctor:</strong> {prescription.doctor_name}</p>
                    
                    <div className="mt-3">
                      <p className="mb-1"><strong>Medications:</strong></p>
                      <ul className="ps-3">
                        {prescription.items.map((item, index) => (
                          <li key={index}>
                            {item.medication_name} - {item.dosage}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="mt-3">
                      <Link to={`/patient/prescriptions/${prescription._id}`} className="btn btn-sm btn-primary">
                        View Details
                      </Link>
                    </div>
                  </Card.Body>
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
                <Card.Title>View Medication History</Card.Title>
                <Card.Text>
                  Access your complete medication history and prescription records.
                </Card.Text>
                <Link to="/patient/prescriptions" className="btn btn-primary">
                  View Medications
                </Link>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </section>
    </Layout>
  );
};

export default PatientDashboard; 