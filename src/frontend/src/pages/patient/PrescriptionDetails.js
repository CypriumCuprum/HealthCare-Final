import React, { useState, useEffect } from 'react';
import { Card, Badge, Row, Col, Table, Alert } from 'react-bootstrap';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { patientPharmacyService } from '../../services/api';

const PrescriptionDetails = () => {
  const { id } = useParams();
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  const [prescription, setPrescription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch prescription details
  useEffect(() => {
    const fetchPrescriptionDetails = async () => {
      try {
        const response = await patientPharmacyService.getPrescriptionDetails(id);
        setPrescription(response.data);
      } catch (err) {
        console.error('Error fetching prescription details:', err);
        setError('Failed to load prescription details');
        
        // For development, use mock data if API fails
        setPrescription({
          _id: id,
          patient_id: currentUser.id,
          patient_name: `${currentUser.first_name} ${currentUser.last_name}`,
          doctor_id: 2,
          doctor_name: 'Dr. Smith',
          date_prescribed: new Date().toISOString(),
          status: 'VERIFIED',
          notes_for_pharmacist: 'Please dispense generic if available.',
          items: [
            {
              item_id: 'item1',
              medication_id: 'med1',
              medication_name: 'Amoxicillin 500mg',
              dosage: '1 tablet',
              frequency: '3 times a day',
              duration_days: 7,
              instructions: 'Take with food.',
              quantity_prescribed: 21
            }
          ],
          dispense_history: [{
            dispense_log_id: 'disp1',
            pharmacist_id: 3,
            date_dispensed: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            dispensed_items: [
              { item_id_ref: 'item1', quantity_dispensed: 21 }
            ]
          }]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchPrescriptionDetails();
  }, [id, currentUser]);

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

  if (loading) {
    return (
      <Layout>
        <p>Loading prescription details...</p>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <Alert variant="danger">{error}</Alert>
        <div className="mt-3">
          <Link to="/patient/prescriptions" className="btn btn-primary">
            Back to Prescriptions
          </Link>
        </div>
      </Layout>
    );
  }

  if (!prescription) {
    return (
      <Layout>
        <Alert variant="warning">Prescription not found.</Alert>
        <div className="mt-3">
          <Link to="/patient/prescriptions" className="btn btn-primary">
            Back to Prescriptions
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <div>
          <h2>Prescription Details</h2>
          <p className="text-muted">Prescribed on {formatDate(prescription.date_prescribed)}</p>
        </div>
        <div>
          <Link to="/patient/prescriptions" className="btn btn-outline-primary">
            Back to Prescriptions
          </Link>
        </div>
      </div>

      <Row className="mb-4">
        <Col md={6}>
          <Card className="mb-4 mb-md-0">
            <Card.Body>
              <Card.Title>Prescription Information</Card.Title>
              
              <div className="mb-3">
                <Badge bg={getStatusBadgeVariant(prescription.status)} className="fs-6">
                  {prescription.status.replace(/_/g, ' ')}
                </Badge>
              </div>
              
              <Table className="table-borderless">
                <tbody>
                  <tr>
                    <td className="fw-bold">Patient:</td>
                    <td>{prescription.patient_name}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Doctor:</td>
                    <td>{prescription.doctor_name}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Date:</td>
                    <td>{formatDate(prescription.date_prescribed)}</td>
                  </tr>
                  {prescription.notes_for_pharmacist && (
                    <tr>
                      <td className="fw-bold">Notes:</td>
                      <td>{prescription.notes_for_pharmacist}</td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card>
            <Card.Body>
              <Card.Title>Dispense History</Card.Title>
              
              {prescription.dispense_history && prescription.dispense_history.length > 0 ? (
                prescription.dispense_history.map((dispense, index) => (
                  <div key={dispense.dispense_log_id || index} className="border-bottom mb-3 pb-3">
                    <p className="mb-1">
                      <strong>Dispensed:</strong> {formatDate(dispense.date_dispensed)}
                    </p>
                    <p className="mb-0 text-muted">
                      Items dispensed: {dispense.dispensed_items.reduce((total, item) => total + item.quantity_dispensed, 0)}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-muted">No dispense history available.</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card>
        <Card.Body>
          <Card.Title>Medications</Card.Title>
          
          <Table responsive className="mt-3">
            <thead>
              <tr>
                <th>Medication</th>
                <th>Dosage</th>
                <th>Frequency</th>
                <th>Duration</th>
                <th>Quantity</th>
                <th>Instructions</th>
              </tr>
            </thead>
            <tbody>
              {prescription.items.map((item, index) => (
                <tr key={item.item_id || index}>
                  <td>{item.medication_name}</td>
                  <td>{item.dosage}</td>
                  <td>{item.frequency}</td>
                  <td>{item.duration_days ? `${item.duration_days} days` : 'N/A'}</td>
                  <td>{item.quantity_prescribed}</td>
                  <td>{item.instructions || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </Layout>
  );
};

export default PrescriptionDetails; 