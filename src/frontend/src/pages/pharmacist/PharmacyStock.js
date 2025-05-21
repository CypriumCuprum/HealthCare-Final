import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Form, Table, Row, Col, Alert, Modal } from 'react-bootstrap';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { pharmacistPharmacyService } from '../../services/api';

const PharmacyStock = () => {
  const { currentUser } = useAuth();
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [search, setSearch] = useState('');
  const [filterLowStock, setFilterLowStock] = useState(false);
  
  // State for updating stock modal
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [selectedMedication, setSelectedMedication] = useState(null);
  const [updateQuantity, setUpdateQuantity] = useState(0);

  // Fetch medications data from API
  useEffect(() => {
    const fetchMedications = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await pharmacistPharmacyService.getPharmacyStock();
        setMedications(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching inventory:', err);
        setError('Failed to load inventory data. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchMedications();
  }, []);

  // Format date in a user-friendly way
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Check if medication is low on stock
  const isLowStock = (medication) => {
    return medication.quantity_on_hand <= medication.reorder_level;
  };

  // Filter medications based on search and low stock filter
  const filteredMedications = medications.filter(med => {
    // Apply search filter
    const matchesSearch = search === '' || 
      med.medication_name.toLowerCase().includes(search.toLowerCase()) ||
      med.medication_code.toLowerCase().includes(search.toLowerCase());
    
    // Apply low stock filter
    const matchesLowStock = !filterLowStock || isLowStock(med);
    
    return matchesSearch && matchesLowStock;
  });

  // Open update stock modal
  const openUpdateModal = (medication) => {
    console.log(medication) 
    setSelectedMedication(medication);
    setUpdateQuantity(0);
    setShowUpdateModal(true);
  };

  // Close update stock modal
  const closeUpdateModal = () => {
    setSelectedMedication(null);
    setUpdateQuantity(0);
    setShowUpdateModal(false);
  };

  // Handle stock update
  const handleUpdateStock = async () => {
    if (!selectedMedication || updateQuantity <= 0) return;
    
    setLoading(true);
    setError(null);
    
  
    try {
      const stockData = { 
        quantity_to_add: updateQuantity,
        batch_number: `B${Math.floor(Math.random() * 1000)}`,
        expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      };
      
      const response = await pharmacistPharmacyService.updateStock(
        selectedMedication.id, 
        stockData
      );
      console.log(response)

      // Update local state with new quantity
      setMedications(prevMeds => 
        prevMeds.map(med => 
          med._id === selectedMedication._id 
            ? response.data  // Use the response data from API
            : med
        )
      );
      
      setSuccess(`Successfully added ${updateQuantity} units of ${selectedMedication.medication_name}`);
      closeUpdateModal();
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccess(null);
      }, 3000);

      // refresh the page
      window.location.reload();
    } catch (err) {
      console.error('Error updating stock:', err);
      setError('Failed to update medication stock. Please try again later.');
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <h2>Pharmacy Inventory</h2>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Search</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Search by name or code"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mt-md-4">
                <Form.Check
                  type="checkbox"
                  label="Show only low stock items"
                  checked={filterLowStock}
                  onChange={(e) => setFilterLowStock(e.target.checked)}
                />
              </Form.Group>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {loading && medications.length === 0 ? (
        <p>Loading inventory...</p>
      ) : filteredMedications.length === 0 ? (
        <Card className="p-4">
          <Card.Body className="text-center">
            <h5>No medications found</h5>
            <p className="text-muted">
              Try adjusting your search filters.
            </p>
          </Card.Body>
        </Card>
      ) : (
        <Table responsive hover>
          <thead>
            <tr>
              <th>Code</th>
              <th>Medication</th>
              <th className="text-center">Quantity</th>
              <th className="text-center">Reorder Level</th>
              <th>Last Stocked</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredMedications.map(medication => (
              <tr key={medication._id}>
                <td>{medication.medication_code}</td>
                <td>{medication.medication_name}</td>
                <td className="text-center">
                  {isLowStock(medication) ? (
                    <Badge bg="danger">{medication.quantity_on_hand}</Badge>
                  ) : (
                    medication.quantity_on_hand
                  )}
                </td>
                <td className="text-center">{medication.reorder_level}</td>
                <td>{formatDate(medication.last_stocked_date)}</td>
                <td>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => openUpdateModal(medication)}
                  >
                    Update Stock
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {/* Update Stock Modal */}
      <Modal show={showUpdateModal} onHide={closeUpdateModal}>
        <Modal.Header closeButton>
          <Modal.Title>Update Stock</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedMedication && (
            <>
              <p>
                <strong>Medication:</strong> {selectedMedication.medication_name}<br />
                <strong>Current Stock:</strong> {selectedMedication.quantity_on_hand} units<br />
                <strong>Reorder Level:</strong> {selectedMedication.reorder_level} units
              </p>
              
              <Form.Group>
                <Form.Label>Quantity to Add</Form.Label>
                <Form.Control
                  type="number"
                  min="1"
                  value={updateQuantity}
                  onChange={(e) => setUpdateQuantity(parseInt(e.target.value) || 0)}
                />
              </Form.Group>
              
              <Form.Group className="mt-3">
                <Form.Label>Batch Number</Form.Label>
                <Form.Control
                  type="text"
                  defaultValue={`B${Math.floor(Math.random() * 1000)}`}
                  disabled
                />
              </Form.Group>
              
              <Form.Group className="mt-3">
                <Form.Label>Expiry Date</Form.Label>
                <Form.Control
                  type="date"
                  defaultValue={new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
                />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeUpdateModal} disabled={loading}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleUpdateStock} 
            disabled={loading || updateQuantity <= 0}
          >
            {loading ? 'Updating...' : 'Update Stock'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Layout>
  );
};

export default PharmacyStock; 