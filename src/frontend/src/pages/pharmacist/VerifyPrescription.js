import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Form, Row, Col, Alert } from 'react-bootstrap';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { pharmacistPharmacyService } from '../../services/api';

const VerifyPrescription = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  const [prescription, setPrescription] = useState(null);
  const [stockInfo, setStockInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [notes, setNotes] = useState('');

  // Fetch prescription and stock data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Get prescription details
        const prescriptionResponse = await pharmacistPharmacyService.getPrescriptionDetails(id);
        setPrescription(prescriptionResponse.data);
        
        // Get stock info for all medications in prescription
        const stockResponse = await pharmacistPharmacyService.getPharmacyStock();
        
        // Convert array to lookup object by medication_id
        const stockLookup = {};
        stockResponse.data.forEach(item => {
          stockLookup[item.medication_id] = {
            quantity_on_hand: item.quantity_on_hand,
            reorder_level: item.reorder_level
          };
        });
        
        setStockInfo(stockLookup);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching prescription data:', err);
        setError('Failed to load prescription details. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchData();
  }, [id]);

  // Format date in a user-friendly way
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Check if medication is in stock
  const isInStock = (medication_id, quantity_needed) => {
    return stockInfo[medication_id] && 
           stockInfo[medication_id].quantity_on_hand >= quantity_needed;
  };

  // Handle verify prescription
  const handleVerify = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await pharmacistPharmacyService.verifyPrescription(id);
      
      setSuccess(true);
      setTimeout(() => {
        navigate('/pharmacist/prescriptions/pending');
      }, 2000);
    } catch (err) {
      console.error('Error verifying prescription:', err);
      setError('Failed to verify prescription. Please try again later.');
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <h2>Verify Prescription</h2>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">Prescription verified successfully!</Alert>}

      {loading && !prescription ? (
        <p>Loading prescription details...</p>
      ) : !prescription ? (
        <Alert variant="danger">Prescription not found</Alert>
      ) : (
        <>
          <Card className="mb-4">
            <Card.Body>
              <Row>
                <Col md={6}>
                  <h5>Patient Information</h5>
                  <p className="mb-1"><strong>Name:</strong> {prescription.patient_name}</p>
                  <p className="mb-1"><strong>ID:</strong> {prescription.patient_id}</p>
                </Col>
                <Col md={6}>
                  <h5>Prescription Details</h5>
                  <p className="mb-1"><strong>Prescribed By:</strong> {prescription.doctor_name}</p>
                  <p className="mb-1"><strong>Date:</strong> {formatDate(prescription.date_prescribed)}</p>
                  <p className="mb-1">
                    <strong>Status:</strong>{' '}
                    <Badge bg="warning">PENDING VERIFICATION</Badge>
                  </p>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Medications</h5>
            </Card.Header>
            <Card.Body>
              {prescription.items.map((item, index) => (
                <div key={index} className="p-3 border rounded mb-3">
                  <Row>
                    <Col md={9}>
                      <h5>{item.medication_name}</h5>
                      <Row>
                        <Col md={4}>
                          <p className="mb-1"><strong>Dosage:</strong> {item.dosage}</p>
                        </Col>
                        <Col md={4}>
                          <p className="mb-1"><strong>Frequency:</strong> {item.frequency}</p>
                        </Col>
                        <Col md={4}>
                          <p className="mb-1"><strong>Duration:</strong> {item.duration_days} days</p>
                        </Col>
                      </Row>
                      <p className="mb-1"><strong>Instructions:</strong> {item.instructions}</p>
                      <p className="mb-1"><strong>Quantity:</strong> {item.quantity_prescribed}</p>
                    </Col>
                    <Col md={3} className="text-end">
                      {isInStock(item.medication_id, item.quantity_prescribed) ? (
                        <Badge bg="success">In Stock</Badge>
                      ) : (
                        <Badge bg="danger">Out of Stock</Badge>
                      )}
                      <p className="mt-2 mb-0">
                        <small>
                          Stock: {stockInfo[item.medication_id]?.quantity_on_hand || 0} units
                        </small>
                      </p>
                    </Col>
                  </Row>
                </div>
              ))}
            </Card.Body>
          </Card>

          {prescription.notes_for_pharmacist && (
            <Card className="mb-4">
              <Card.Header>
                <h5 className="mb-0">Notes from Doctor</h5>
              </Card.Header>
              <Card.Body>
                <p className="mb-0">{prescription.notes_for_pharmacist}</p>
              </Card.Body>
            </Card>
          )}
          
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Pharmacist Notes</h5>
            </Card.Header>
            <Card.Body>
              <Form.Group>
                <Form.Label>Add notes (for internal use)</Form.Label>
                <Form.Control 
                  as="textarea" 
                  rows={3} 
                  value={notes} 
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add any notes or observations..."
                  disabled={loading || success}
                />
              </Form.Group>
            </Card.Body>
          </Card>

          <div className="d-flex justify-content-between">
            <Button 
              variant="secondary" 
              onClick={() => navigate('/pharmacist/prescriptions/pending')}
              disabled={loading}
            >
              Back to List
            </Button>
            <Button 
              variant="primary" 
              onClick={handleVerify}
              disabled={loading || success}
            >
              {loading ? 'Verifying...' : 'Verify Prescription'}
            </Button>
          </div>
        </>
      )}
    </Layout>
  );
};

export default VerifyPrescription; 