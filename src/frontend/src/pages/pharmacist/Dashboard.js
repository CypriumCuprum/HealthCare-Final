import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Badge, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';
import { pharmacistPharmacyService } from '../../services/api';

const PharmacistDashboard = () => {
  const { currentUser } = useAuth();
  const [pendingPrescriptions, setPendingPrescriptions] = useState([]);
  const [lowStockItems, setLowStockItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data for the dashboard
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch pending prescriptions
        const prescriptionsResponse = await pharmacistPharmacyService.getPendingPrescriptions();
        const sortedPrescriptions = prescriptionsResponse.data.sort(
          (a, b) => new Date(a.date_prescribed) - new Date(b.date_prescribed)
        ).slice(0, 5); // Get 5 oldest pending prescriptions
        setPendingPrescriptions(sortedPrescriptions);
        
        // Fetch pharmacy stock
        const stockResponse = await pharmacistPharmacyService.getPharmacyStock();
        // Filter for low stock items (below reorder level)
        const lowStock = stockResponse.data.filter(item => item.quantity_on_hand <= item.reorder_level);
        setLowStockItems(lowStock);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
        
        // For development, use mock data if API fails
        setPendingPrescriptions([
          {
            id: 'presc1',
            patient_name: 'John Doe',
            doctor_name: 'Dr. Smith',
            date_prescribed: new Date().toISOString(),
            status: 'PENDING_VERIFICATION',
            items: [
              { medication_name: 'Amoxicillin 500mg', quantity_prescribed: 21 }
            ]
          },
          {
            id: 'presc2',
            patient_name: 'Jane Smith',
            doctor_name: 'Dr. Johnson',
            date_prescribed: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'PENDING_VERIFICATION',
            items: [
              { medication_name: 'Lisinopril 10mg', quantity_prescribed: 30 }
            ]
          },
          {
            id: 'presc3',
            patient_name: 'Robert Brown',
            doctor_name: 'Dr. Williams',
            date_prescribed: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'VERIFIED',
            items: [
              { medication_name: 'Metformin 500mg', quantity_prescribed: 60 }
            ]
          }
        ]);
        
        setLowStockItems([
          {
            id: 'med1',
            medication_name: 'Amoxicillin 500mg',
            quantity_on_hand: 25,
            reorder_level: 50
          },
          {
            id: 'med2',
            medication_name: 'Lisinopril 10mg',
            quantity_on_hand: 15,
            reorder_level: 30
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Format date in a user-friendly way
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <Layout>
      <div className="mb-4">
        <h2>Pharmacist Dashboard</h2>
        <p className="text-muted">Welcome, {currentUser.first_name}! Manage prescriptions and inventory.</p>
      </div>

      <div className="dashboard-stats">
        <Card className="stat-card" bg="info" text="white">
          <h3>{pendingPrescriptions.filter(p => p.status === 'PENDING_VERIFICATION').length}</h3>
          <p>Pending Verifications</p>
        </Card>
        <Card className="stat-card" bg="warning" text="white">
          <h3>{pendingPrescriptions.filter(p => p.status === 'VERIFIED').length}</h3>
          <p>Ready for Dispensing</p>
        </Card>
        <Card className="stat-card" bg="danger" text="white">
          <h3>{lowStockItems.length}</h3>
          <p>Low Stock Items</p>
        </Card>
      </div>

      <Row className="mt-4">
        <Col lg={8}>
          <Card className="mb-4">
            <Card.Header>
              <div className="d-flex justify-content-between align-items-center">
                <h4 className="mb-0">Pending Prescriptions</h4>
                <Link to="/pharmacist/prescriptions/pending" className="btn btn-sm btn-primary">
                  View All
                </Link>
              </div>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <p>Loading prescriptions...</p>
              ) : error ? (
                <p className="text-danger">{error}</p>
              ) : pendingPrescriptions.length === 0 ? (
                <p className="text-muted">No pending prescriptions.</p>
              ) : (
                <div>
                  {pendingPrescriptions.map((prescription) => (
                    <div key={prescription.id} className="pharmacy-item mb-3">
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <div>
                          <h5>{prescription.patient_name}</h5>
                          <p className="text-muted mb-0">
                            Prescribed by {prescription.doctor_name} on {formatDate(prescription.date_prescribed)}
                          </p>
                        </div>
                        <Badge 
                          bg={prescription.status === 'PENDING_VERIFICATION' ? 'warning' : 'info'}
                        >
                          {prescription.status.replace('_', ' ')}
                        </Badge>
                      </div>
                      <div className="d-flex justify-content-between align-items-center mt-3">
                        <div>
                          <small className="text-muted">
                            {prescription.items.length} medication(s)
                          </small>
                        </div>
                        <div>
                          {prescription.status === 'PENDING_VERIFICATION' ? (
                            <Link 
                              to={`/pharmacist/prescriptions/${prescription.id}/verify`} 
                              className="btn btn-sm btn-outline-primary me-2"
                            >
                              Verify
                            </Link>
                          ) : (
                            <Link 
                              to={`/pharmacist/prescriptions/${prescription.id}/dispense`} 
                              className="btn btn-sm btn-outline-success me-2"
                            >
                              Dispense
                            </Link>
                          )}
                          <Link 
                            to={`/patient/prescriptions/${prescription.id}`} 
                            className="btn btn-sm btn-outline-secondary"
                          >
                            View Details
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={4}>
          <Card className="mb-4">
            <Card.Header>
              <div className="d-flex justify-content-between align-items-center">
                <h4 className="mb-0">Low Stock Items</h4>
                <Link to="/pharmacist/stock" className="btn btn-sm btn-primary">
                  Manage Inventory
                </Link>
              </div>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <p>Loading inventory data...</p>
              ) : error ? (
                <p className="text-danger">{error}</p>
              ) : lowStockItems.length === 0 ? (
                <p className="text-muted">No low stock items.</p>
              ) : (
                <div>
                  {lowStockItems.map((item) => (
                    <div key={item.id} className="pharmacy-item">
                      <h5>{item.medication_name}</h5>
                      <div className="d-flex justify-content-between">
                        <p className="mb-0">
                          <strong>Current Stock:</strong> {item.quantity_on_hand}
                        </p>
                        <p className="mb-0">
                          <strong>Reorder Level:</strong> {item.reorder_level}
                        </p>
                      </div>
                      <div className="progress mt-2" style={{ height: '10px' }}>
                        <div 
                          className={`progress-bar ${item.quantity_on_hand / item.reorder_level < 0.5 ? 'bg-danger' : 'bg-warning'}`}
                          role="progressbar" 
                          style={{ width: `${(item.quantity_on_hand / item.reorder_level) * 100}%` }} 
                          aria-valuenow={item.quantity_on_hand} 
                          aria-valuemin="0" 
                          aria-valuemax={item.reorder_level}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
          
          <Card>
            <Card.Header>
              <h4 className="mb-0">Quick Actions</h4>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Link to="/pharmacist/prescriptions/pending" className="btn btn-primary">
                  Verify Prescriptions
                </Link>
                <Link to="/pharmacist/stock" className="btn btn-outline-primary">
                  Update Inventory
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Layout>
  );
};

export default PharmacistDashboard; 