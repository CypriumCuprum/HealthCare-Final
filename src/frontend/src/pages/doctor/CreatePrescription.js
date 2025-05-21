import React, { useState, useEffect } from 'react';
import { Card, Button, Form, Alert, Table, Row, Col } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { doctorPharmacyService } from '../../services/api';

const CreatePrescription = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Patient search
  const [patientSearch, setPatientSearch] = useState('');
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientSearchLoading, setPatientSearchLoading] = useState(false);
  
  // Medication search
  const [searchMedication, setSearchMedication] = useState('');
  const [medications, setMedications] = useState([]);
  const [medicationsLoading, setMedicationsLoading] = useState(false);
  
  // Prescription items
  const [items, setItems] = useState([]);
  const [currentItem, setCurrentItem] = useState({
    medication_id: '',
    medication_name: '',
    dosage: '',
    frequency: '',
    duration_days: 7,
    quantity_prescribed: 0,
    instructions: ''
  });

  // Fetch all medications on component mount
  useEffect(() => {
    const fetchMedications = async () => {
      setMedicationsLoading(true);
      
      try {
        const response = await doctorPharmacyService.getMedications();
        setMedications(response.data);
        setMedicationsLoading(false);
      } catch (err) {
        console.error('Error fetching medications:', err);
        setError('Failed to load medications. Please try again later.');
        setMedicationsLoading(false);
      }
    };
    
    fetchMedications();
  }, []);
  
  // Handle patient search
  useEffect(() => {
    const searchPatients = async () => {
      if (patientSearch.length < 2) {
        setPatients([]);
        return;
      }
      
      setPatientSearchLoading(true);
      
      try {
        const response = await doctorPharmacyService.searchPatients(patientSearch);
        setPatients(response.data);
        setPatientSearchLoading(false);
      } catch (err) {
        console.error('Error searching patients:', err);
        setPatientSearchLoading(false);
      }
    };
    
    const timeoutId = setTimeout(searchPatients, 500);
    return () => clearTimeout(timeoutId);
  }, [patientSearch]);

  // Handle selecting a patient
  const handleSelectPatient = (patient) => {
    setSelectedPatient(patient);
    setPatients([]);
    setPatientSearch('');
  };

  // Handle selecting a medication
  const handleSelectMedication = (medication) => {
    setCurrentItem({
      ...currentItem,
      medication_id: medication._id,
      medication_name: medication.name,
      dosage: medication.dosage_form ? `1 ${medication.dosage_form.toLowerCase()}` : ''
    });
    setSearchMedication('');
  };

  // Handle adding a medication to the prescription
  const handleAddMedication = () => {
    if (!currentItem.medication_id || !currentItem.dosage || !currentItem.frequency) {
      setError('Please fill in all required medication fields');
      return;
    }
    
    // Generate a temporary ID for this item
    const newItem = {
      ...currentItem,
      item_id: `item_${Date.now()}`
    };
    
    setItems(prevItems => [...prevItems, newItem]);
    
    // Reset current item form
    setCurrentItem({
      medication_id: '',
      medication_name: '',
      dosage: '',
      frequency: '',
      duration_days: 7,
      quantity_prescribed: 0,
      instructions: ''
    });
  };

  // Handle removing a medication from the prescription
  const handleRemoveMedication = (index) => {
    setItems(prevItems => prevItems.filter((_, i) => i !== index));
  };

  // Handle form input changes for medication
  const handleItemChange = (e) => {
    const { name, value } = e.target;
    setCurrentItem({
      ...currentItem,
      [name]: name === 'duration_days' || name === 'quantity_prescribed' 
        ? parseInt(value) || 0 
        : value
    });
  };

  // Calculate quantity based on duration and frequency
  const calculateQuantity = () => {
    let frequencyPerDay = 0;
    const { frequency, duration_days } = currentItem;
    
    if (frequency === 'Once daily' || frequency === 'Every night' || frequency === 'Every morning') {
      frequencyPerDay = 1;
    } else if (frequency === 'Twice daily') {
      frequencyPerDay = 2;
    } else if (frequency === 'Three times a day') {
      frequencyPerDay = 3;
    } else if (frequency === 'Four times a day') {
      frequencyPerDay = 4;
    } else if (frequency === 'Every 4 hours') {
      frequencyPerDay = 6;
    } else if (frequency === 'Every 6 hours') {
      frequencyPerDay = 4;
    } else if (frequency === 'Every 8 hours') {
      frequencyPerDay = 3;
    } else if (frequency === 'Every 12 hours') {
      frequencyPerDay = 2;
    } else {
      // For as needed, we default to a lower number
      frequencyPerDay = 1;
    }
    
    const calculatedQuantity = frequencyPerDay * duration_days;
    
    setCurrentItem({
      ...currentItem,
      quantity_prescribed: calculatedQuantity
    });
  };

  // Calculate quantity when frequency or duration changes
  useEffect(() => {
    if (currentItem.frequency && currentItem.duration_days) {
      calculateQuantity();
    }
  }, [currentItem.frequency, currentItem.duration_days]);

  // Handle creating the prescription
  const handleCreatePrescription = async () => {
    if (!selectedPatient) {
      setError('Please select a patient');
      return;
    }
    
    if (items.length === 0) {
      setError('Please add at least one medication');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const prescriptionData = {
        patient_id: selectedPatient.id,
        doctor_id: currentUser.id,
        notes_for_pharmacist: document.getElementById('notes_for_pharmacist').value,
        items: items.map(item => ({
          medication_id: item.medication_id,
          dosage: item.dosage,
          frequency: item.frequency,
          duration_days: item.duration_days,
          quantity_prescribed: item.quantity_prescribed,
          instructions: item.instructions
        }))
      };
      
      const response = await doctorPharmacyService.createPrescription(prescriptionData);
      
      setSuccess(true);
      setTimeout(() => {
        navigate('/doctor/prescriptions');
      }, 2000);
    } catch (err) {
      console.error('Error creating prescription:', err);
      setError('Failed to create prescription. Please try again later.');
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <h2>Create New Prescription</h2>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">Prescription created successfully!</Alert>}

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Patient Information</h5>
        </Card.Header>
        <Card.Body>
          {selectedPatient ? (
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <p className="mb-1"><strong>Name:</strong> {selectedPatient.first_name} {selectedPatient.last_name}</p>
                <p className="mb-0"><strong>ID:</strong> {selectedPatient.id}</p>
              </div>
              <Button 
                variant="outline-secondary" 
                size="sm"
                onClick={() => setSelectedPatient(null)}
              >
                Change Patient
              </Button>
            </div>
          ) : (
            <Form>
              <Form.Group>
                <Form.Label>Search Patient</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Enter patient name or ID"
                  value={patientSearch}
                  onChange={(e) => setPatientSearch(e.target.value)}
                />
                {patientSearchLoading && <p className="mt-2 mb-0">Searching...</p>}
                {patients.length > 0 && (
                  <div className="mt-2 border rounded">
                    {patients.map(patient => (
                      <div 
                        key={patient.id} 
                        className="p-2 border-bottom patient-result"
                        onClick={() => handleSelectPatient(patient)}
                        style={{ cursor: 'pointer' }}
                      >
                        <p className="mb-0">{patient.first_name} {patient.last_name} (ID: {patient.id})</p>
                      </div>
                    ))}
                  </div>
                )}
              </Form.Group>
            </Form>
          )}
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Medication</h5>
        </Card.Header>
        <Card.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Search Medication</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Search by name or code"
                    value={searchMedication}
                    onChange={(e) => setSearchMedication(e.target.value)}
                    disabled={!selectedPatient}
                  />
                  {medicationsLoading && <p className="mt-2 mb-0">Loading...</p>}
                  {searchMedication && medications.length > 0 && (
                    <div className="mt-2 border rounded">
                      {medications
                        .filter(med => 
                          med.name.toLowerCase().includes(searchMedication.toLowerCase()) ||
                          med.medication_code.toLowerCase().includes(searchMedication.toLowerCase())
                        )
                        .slice(0, 5)
                        .map(medication => (
                          <div 
                            key={medication._id} 
                            className="p-2 border-bottom medication-result"
                            onClick={() => handleSelectMedication(medication)}
                            style={{ cursor: 'pointer' }}
                          >
                            <p className="mb-0">{medication.name} ({medication.medication_code})</p>
                          </div>
                        ))}
                    </div>
                  )}
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Selected Medication</Form.Label>
                  <Form.Control
                    type="text"
                    value={currentItem.medication_name}
                    readOnly
                    placeholder="No medication selected"
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Dosage</Form.Label>
                  <Form.Control
                    type="text"
                    name="dosage"
                    value={currentItem.dosage}
                    onChange={handleItemChange}
                    placeholder="e.g., 1 tablet"
                    disabled={!currentItem.medication_id}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Frequency</Form.Label>
                  <Form.Select
                    name="frequency"
                    value={currentItem.frequency}
                    onChange={handleItemChange}
                    disabled={!currentItem.medication_id}
                  >
                    <option value="">Select frequency</option>
                    <option value="Once daily">Once daily</option>
                    <option value="Twice daily">Twice daily</option>
                    <option value="Three times a day">Three times a day</option>
                    <option value="Four times a day">Four times a day</option>
                    <option value="Every morning">Every morning</option>
                    <option value="Every night">Every night</option>
                    <option value="Every 4 hours">Every 4 hours</option>
                    <option value="Every 6 hours">Every 6 hours</option>
                    <option value="Every 8 hours">Every 8 hours</option>
                    <option value="Every 12 hours">Every 12 hours</option>
                    <option value="As needed">As needed (PRN)</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Duration (days)</Form.Label>
                  <Form.Control
                    type="number"
                    name="duration_days"
                    value={currentItem.duration_days}
                    onChange={handleItemChange}
                    min="1"
                    disabled={!currentItem.medication_id}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Special Instructions</Form.Label>
                  <Form.Control
                    type="text"
                    name="instructions"
                    value={currentItem.instructions}
                    onChange={handleItemChange}
                    placeholder="e.g., Take with food"
                    disabled={!currentItem.medication_id}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Quantity</Form.Label>
                  <Form.Control
                    type="number"
                    name="quantity_prescribed"
                    value={currentItem.quantity_prescribed}
                    onChange={handleItemChange}
                    min="1"
                    disabled={!currentItem.medication_id}
                  />
                  <Form.Text className="text-muted">
                    Suggested quantity based on frequency and duration
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>

            <div className="mt-3">
              <Button 
                variant="secondary" 
                onClick={handleAddMedication}
                disabled={!currentItem.medication_id || !currentItem.dosage || !currentItem.frequency || loading || success}
              >
                Add to Prescription
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>

      {items.length > 0 && (
        <Card className="mb-4">
          <Card.Header>
            <h5 className="mb-0">Prescription Items ({items.length})</h5>
          </Card.Header>
          <Card.Body>
            <Table responsive>
              <thead>
                <tr>
                  <th>Medication</th>
                  <th>Dosage</th>
                  <th>Frequency</th>
                  <th>Duration</th>
                  <th>Quantity</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => (
                  <tr key={item.item_id}>
                    <td>{item.medication_name}</td>
                    <td>{item.dosage}</td>
                    <td>{item.frequency}</td>
                    <td>{item.duration_days} days</td>
                    <td>{item.quantity_prescribed}</td>
                    <td>
                      <Button 
                        variant="outline-danger" 
                        size="sm"
                        onClick={() => handleRemoveMedication(index)}
                        disabled={loading || success}
                      >
                        Remove
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      )}

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Notes for Pharmacist</h5>
        </Card.Header>
        <Card.Body>
          <Form.Control
            as="textarea"
            id="notes_for_pharmacist"
            rows={3}
            placeholder="Enter any additional notes for the pharmacist..."
            disabled={loading || success}
          />
        </Card.Body>
      </Card>

      <div className="d-flex justify-content-between">
        <Button 
          variant="secondary" 
          onClick={() => navigate('/doctor/prescriptions')}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={handleCreatePrescription}
          disabled={!selectedPatient || items.length === 0 || loading || success}
        >
          {loading ? 'Creating...' : 'Create Prescription'}
        </Button>
      </div>
    </Layout>
  );
};

export default CreatePrescription; 