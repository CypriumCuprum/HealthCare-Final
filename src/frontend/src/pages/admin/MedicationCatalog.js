import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Form, Table, Row, Col, Alert, Modal } from 'react-bootstrap';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { adminService } from '../../services/api';

const MedicationCatalog = () => {
  const { currentUser } = useAuth();
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [search, setSearch] = useState('');
  
  // State for medication modal
  const [showMedicationModal, setShowMedicationModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedMedication, setSelectedMedication] = useState(null);
  const [medicationForm, setMedicationForm] = useState({
    medication_code: '',
    name: '',
    generic_name: '',
    manufacturer: '',
    description: '',
    unit_price: 0,
    dosage_form: '',
    strength: ''
  });

  // Fetch medications from API
  useEffect(() => {
    const fetchMedications = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await adminService.getMedications();
        setMedications(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching medications:', err);
        setError('Failed to load medication catalog. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchMedications();
  }, []);

  // Filter medications based on search
  const filteredMedications = medications.filter(med => 
    search === '' || 
    med.name.toLowerCase().includes(search.toLowerCase()) ||
    med.medication_code.toLowerCase().includes(search.toLowerCase()) ||
    med.generic_name.toLowerCase().includes(search.toLowerCase())
  );

  // Open medication modal for creating new medication
  const openAddMedicationModal = () => {
    setIsEditing(false);
    setSelectedMedication(null);
    setMedicationForm({
      medication_code: '',
      name: '',
      generic_name: '',
      manufacturer: '',
      description: '',
      unit_price: 0,
      dosage_form: '',
      strength: ''
    });
    setShowMedicationModal(true);
  };

  // Open medication modal for editing existing medication
  const openEditMedicationModal = (medication) => {
    setIsEditing(true);
    setSelectedMedication(medication);
    setMedicationForm({
      medication_code: medication.medication_code,
      name: medication.name,
      generic_name: medication.generic_name,
      manufacturer: medication.manufacturer,
      description: medication.description,
      unit_price: medication.unit_price,
      dosage_form: medication.dosage_form,
      strength: medication.strength
    });
    setShowMedicationModal(true);
  };

  // Close medication modal
  const closeMedicationModal = () => {
    setShowMedicationModal(false);
    setSelectedMedication(null);
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setMedicationForm({
      ...medicationForm,
      [name]: name === 'unit_price' ? parseFloat(value) || 0 : value
    });
  };

  // Handle form submission
  const handleMedicationSubmit = async () => {
    if (!medicationForm.medication_code || !medicationForm.name) {
      setError('Medication code and name are required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      if (isEditing && selectedMedication) {
        // Update existing medication
        const response = await adminService.updateMedication(selectedMedication._id, medicationForm);
        
        // Update local state
        setMedications(prevMeds => 
          prevMeds.map(med => 
            med._id === selectedMedication._id 
              ? response.data
              : med
          )
        );
        
        setSuccess(`Successfully updated ${medicationForm.name}`);
      } else {
        // Create new medication
        const response = await adminService.createMedication(medicationForm);
        
        // Update local state
        setMedications(prevMeds => [...prevMeds, response.data]);
        
        setSuccess(`Successfully added ${medicationForm.name}`);
      }
      
      closeMedicationModal();
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccess(null);
      }, 3000);
    } catch (err) {
      console.error('Error saving medication:', err);
      setError('Failed to save medication. Please try again later.');
      setLoading(false);
    }
  };

  // Handle delete medication
  const handleDeleteMedication = async (medication) => {
    if (!window.confirm(`Are you sure you want to delete ${medication.name}?`)) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await adminService.deleteMedication(medication._id);
      
      // Update local state
      setMedications(prevMeds => prevMeds.filter(med => med._id !== medication._id));
      
      setSuccess(`Successfully deleted ${medication.name}`);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccess(null);
      }, 3000);
    } catch (err) {
      console.error('Error deleting medication:', err);
      setError('Failed to delete medication. Please try again later.');
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <h2>Medication Catalog</h2>
        <Button 
          variant="primary" 
          onClick={openAddMedicationModal}
          disabled={loading}
        >
          Add New Medication
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <Card className="mb-4">
        <Card.Body>
          <Form.Group>
            <Form.Label>Search</Form.Label>
            <Form.Control
              type="text"
              placeholder="Search by name, code, or generic name"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </Form.Group>
        </Card.Body>
      </Card>

      {loading && medications.length === 0 ? (
        <p>Loading medications...</p>
      ) : filteredMedications.length === 0 ? (
        <Card className="p-4">
          <Card.Body className="text-center">
            <h5>No medications found</h5>
            <p className="text-muted">
              Try adjusting your search or add a new medication.
            </p>
          </Card.Body>
        </Card>
      ) : (
        <Table responsive hover>
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Generic Name</th>
              <th>Manufacturer</th>
              <th>Dosage Form</th>
              <th>Strength</th>
              <th>Price</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredMedications.map(medication => (
              <tr key={medication._id}>
                <td>{medication.medication_code}</td>
                <td>{medication.name}</td>
                <td>{medication.generic_name}</td>
                <td>{medication.manufacturer}</td>
                <td>{medication.dosage_form}</td>
                <td>{medication.strength}</td>
                <td>${medication.unit_price.toFixed(2)}</td>
                <td>
                  <Button 
                    variant="outline-primary" 
                    size="sm"
                    className="me-2"
                    onClick={() => openEditMedicationModal(medication)}
                    disabled={loading}
                  >
                    Edit
                  </Button>
                  <Button 
                    variant="outline-danger" 
                    size="sm"
                    onClick={() => handleDeleteMedication(medication)}
                    disabled={loading}
                  >
                    Delete
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {/* Add/Edit Medication Modal */}
      <Modal show={showMedicationModal} onHide={closeMedicationModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{isEditing ? 'Edit Medication' : 'Add New Medication'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Medication Code*</Form.Label>
                  <Form.Control
                    type="text"
                    name="medication_code"
                    value={medicationForm.medication_code}
                    onChange={handleInputChange}
                    required
                    placeholder="e.g., AMOX500"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Name*</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={medicationForm.name}
                    onChange={handleInputChange}
                    required
                    placeholder="e.g., Amoxicillin 500mg"
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Generic Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="generic_name"
                    value={medicationForm.generic_name}
                    onChange={handleInputChange}
                    placeholder="e.g., Amoxicillin"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Manufacturer</Form.Label>
                  <Form.Control
                    type="text"
                    name="manufacturer"
                    value={medicationForm.manufacturer}
                    onChange={handleInputChange}
                    placeholder="e.g., ABC Pharma"
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="description"
                value={medicationForm.description}
                onChange={handleInputChange}
                placeholder="Enter medication description"
              />
            </Form.Group>
            
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Dosage Form</Form.Label>
                  <Form.Select
                    name="dosage_form"
                    value={medicationForm.dosage_form}
                    onChange={handleInputChange}
                  >
                    <option value="">Select form</option>
                    <option value="Tablet">Tablet</option>
                    <option value="Capsule">Capsule</option>
                    <option value="Liquid">Liquid</option>
                    <option value="Injection">Injection</option>
                    <option value="Cream">Cream</option>
                    <option value="Ointment">Ointment</option>
                    <option value="Gel">Gel</option>
                    <option value="Patch">Patch</option>
                    <option value="Inhaler">Inhaler</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Strength</Form.Label>
                  <Form.Control
                    type="text"
                    name="strength"
                    value={medicationForm.strength}
                    onChange={handleInputChange}
                    placeholder="e.g., 500mg"
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Unit Price ($)</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.01"
                    min="0"
                    name="unit_price"
                    value={medicationForm.unit_price}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeMedicationModal} disabled={loading}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleMedicationSubmit} 
            disabled={loading || !medicationForm.medication_code || !medicationForm.name}
          >
            {loading ? 'Saving...' : (isEditing ? 'Update Medication' : 'Add Medication')}
          </Button>
        </Modal.Footer>
      </Modal>
    </Layout>
  );
};

export default MedicationCatalog; 