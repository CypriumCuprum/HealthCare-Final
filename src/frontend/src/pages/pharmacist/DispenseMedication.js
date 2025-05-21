import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Form, Row, Col, Alert, Table } from 'react-bootstrap';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { pharmacistPharmacyService } from '../../services/api';

const DispenseMedication = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  const [prescription, setPrescription] = useState(null);
  const [stockInfo, setStockInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Form state for quantity to dispense
  const [dispensedItems, setDispensedItems] = useState([]);

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
        
        // Initialize dispensed items with full quantity
        const initDispensedItems = prescriptionResponse.data.items.map(item => ({
          item_id_ref: item.item_id,
          medication_id: item.medication_id,
          medication_name: item.medication_name,
          quantity_dispensed: item.quantity_prescribed
        }));
        setDispensedItems(initDispensedItems);
        
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

  // Check if medication is in stock for requested quantity
  const getStockStatus = (medication_id, quantity_needed) => {
    if (!stockInfo[medication_id]) {
      return { status: 'OUT_OF_STOCK', available: 0 };
    }
    
    const available = stockInfo[medication_id].quantity_on_hand;
    
    if (available >= quantity_needed) {
      return { status: 'IN_STOCK', available };
    } else if (available > 0) {
      return { status: 'PARTIAL', available };
    } else {
      return { status: 'OUT_OF_STOCK', available: 0 };
    }
  };

  // Handle changing dispensed quantity
  const handleQuantityChange = (index, value) => {
    const newDispensedItems = [...dispensedItems];
    newDispensedItems[index].quantity_dispensed = Math.max(0, parseInt(value) || 0);
    setDispensedItems(newDispensedItems);
  };

  // Check if we can dispense (at least one item has quantity)
  const canDispense = () => {
    return dispensedItems.some(item => item.quantity_dispensed > 0);
  };

  // Handle dispense medication
  const handleDispense = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Create payload for dispense
      const dispenseData = {
        pharmacist_id: currentUser.id,
        pharmacist_name: currentUser.username,
        items_dispensed: dispensedItems
      };
      
      const response = await pharmacistPharmacyService.dispenseMedication(id, dispenseData);
      
      setSuccess(true);
      setTimeout(() => {
        navigate('/pharmacist/prescriptions/pending');
      }, 2000);
    } catch (err) {
      console.error('Error dispensing medication:', err);
      setError('Failed to dispense medication. Please try again later.');
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <h2>Dispense Medication</h2>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">Medication dispensed successfully!</Alert>}

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
                    <Badge bg="info">VERIFIED</Badge>
                  </p>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Medications to Dispense</h5>
            </Card.Header>
            <Card.Body>
              <Table responsive>
                <thead>
                  <tr>
                    <th>Medication</th>
                    <th>Details</th>
                    <th className="text-center">Stock Status</th>
                    <th className="text-center">Quantity to Dispense</th>
                  </tr>
                </thead>
                <tbody>
                  {prescription.items.map((item, index) => {
                    const stockStatus = getStockStatus(item.medication_id, item.quantity_prescribed);
                    const isOutOfStock = stockStatus.status === 'OUT_OF_STOCK';
                    const isPartial = stockStatus.status === 'PARTIAL';
                    
                    return (
                      <tr key={item.item_id}>
                        <td>
                          <strong>{item.medication_name}</strong>
                        </td>
                        <td>
                          <p className="mb-1">{item.dosage}, {item.frequency}</p>
                          <p className="mb-1">Duration: {item.duration_days} days</p>
                          <p className="mb-1">Instructions: {item.instructions}</p>
                          <p className="mb-0">Prescribed: {item.quantity_prescribed} units</p>
                        </td>
                        <td className="text-center">
                          {isOutOfStock ? (
                            <Badge bg="danger">Out of Stock</Badge>
                          ) : isPartial ? (
                            <Badge bg="warning">Partial Stock: {stockStatus.available}/{item.quantity_prescribed}</Badge>
                          ) : (
                            <Badge bg="success">In Stock: {stockStatus.available} available</Badge>
                          )}
                        </td>
                        <td>
                          <Form.Control
                            type="number"
                            min="0"
                            max={stockStatus.available > item.quantity_prescribed 
                              ? item.quantity_prescribed 
                              : stockStatus.available}
                            value={dispensedItems[index]?.quantity_dispensed || 0}
                            onChange={(e) => handleQuantityChange(index, e.target.value)}
                            disabled={isOutOfStock || loading || success}
                            className="text-center"
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
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
              onClick={handleDispense}
              disabled={loading || success || !canDispense()}
            >
              {loading ? 'Processing...' : 'Dispense Medication'}
            </Button>
          </div>
        </>
      )}
    </Layout>
  );
};

export default DispenseMedication; 