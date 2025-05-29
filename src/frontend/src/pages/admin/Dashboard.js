import React, { useEffect } from 'react';
import { Card, Row, Col, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import { useAuth } from '../../contexts/AuthContext';

const AdminDashboard = () => {
  const { currentUser, isAuthenticated, role } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated || role !== 'ADMIN') {
      console.log('Not authenticated or not admin, redirecting');
      navigate('/login');
    }
  }, [isAuthenticated, role, navigate]);

  if (!isAuthenticated || role !== 'ADMIN') {
    return null;
  }

  return (
    <Layout>
      <div className="mb-4">
        <h2>Admin Dashboard</h2>
        <p className="text-muted">
          Welcome, {currentUser?.first_name || 'Admin'}! Manage system configuration and settings.
        </p>
      </div>

      <div className="dashboard-stats">
        <Card className="stat-card" bg="primary" text="white">
          <h3>7</h3>
          <p>Microservices</p>
        </Card>
        <Card className="stat-card" bg="info" text="white">
          <h3>23</h3>
          <p>Medications</p>
        </Card>
        <Card className="stat-card" bg="success" text="white">
          <h3>4</h3>
          <p>Active Users</p>
        </Card>
      </div>

      <h3 className="section-title mt-4">System Management</h3>
      <Row>
        <Col md={4} className="mb-4">
          <Card className="h-100">
            <Card.Body>
              <Card.Title>Medication Catalog</Card.Title>
              <Card.Text>
                Manage the system-wide medication catalog including new medications, pricing, and inventory settings.
              </Card.Text>
            </Card.Body>
            <Card.Footer className="bg-white">
              <Link to="/admin/medications" className="btn btn-primary w-100">
                Manage Medications
              </Link>
            </Card.Footer>
          </Card>
        </Col>

        <Col md={4} className="mb-4">
          <Card className="h-100">
            <Card.Body>
              <Card.Title>User Management</Card.Title>
              <Card.Text>
                Manage system users including doctors, patients, pharmacists and administrators.
              </Card.Text>
            </Card.Body>
            <Card.Footer className="bg-white">
              <Button className="btn btn-primary w-100" disabled>
                Manage Users
              </Button>
            </Card.Footer>
          </Card>
        </Col>

        <Col md={4} className="mb-4">
          <Card className="h-100">
            <Card.Body>
              <Card.Title>System Configuration</Card.Title>
              <Card.Text>
                Configure system settings, service endpoints, and integration parameters.
              </Card.Text>
            </Card.Body>
            <Card.Footer className="bg-white">
              <Button className="btn btn-primary w-100" disabled>
                System Settings
              </Button>
            </Card.Footer>
          </Card>
        </Col>
      </Row>

      <h3 className="section-title mt-2">Monitoring</h3>
      <Row>
        <Col md={6} className="mb-4">
          <Card className="h-100">
            <Card.Body>
              <Card.Title>Service Health</Card.Title>
              <Card.Text>
                Monitor the health and status of all microservices in the system.
              </Card.Text>
              <div className="mt-3">
                <div className="d-flex justify-content-between mb-2">
                  <span>User Service</span>
                  <span className="badge bg-success">Online</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Pharmacy Service</span>
                  <span className="badge bg-success">Online</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>EHR Service</span>
                  <span className="badge bg-success">Online</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Appointment Service</span>
                  <span className="badge bg-success">Online</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Billing Service</span>
                  <span className="badge bg-success">Online</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Laboratory Service</span>
                  <span className="badge bg-success">Online</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Notification Service</span>
                  <span className="badge bg-success">Online</span>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} className="mb-4">
          <Card className="h-100">
            <Card.Body>
              <Card.Title>System Logs</Card.Title>
              <Card.Text>
                View system logs and error reports across all services.
              </Card.Text>
              <div className="mt-3 small" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                <div className="mb-2 p-2 bg-light rounded">
                  <div className="fw-bold text-primary">[INFO] User Service - 12:45:22</div>
                  <div>User login successful: user_id=2</div>
                </div>
                <div className="mb-2 p-2 bg-light rounded">
                  <div className="fw-bold text-primary">[INFO] Pharmacy Service - 12:43:10</div>
                  <div>Prescription created: prescription_id=presc1</div>
                </div>
                <div className="mb-2 p-2 bg-light rounded">
                  <div className="fw-bold text-primary">[INFO] Notification Service - 12:43:11</div>
                  <div>Notification sent: type=PRESCRIPTION_CREATED, recipient_id=1</div>
                </div>
                <div className="mb-2 p-2 bg-light rounded">
                  <div className="fw-bold text-warning">[WARN] Pharmacy Service - 12:30:05</div>
                  <div>Low stock alert: medication=Amoxicillin 500mg</div>
                </div>
                <div className="mb-2 p-2 bg-light rounded">
                  <div className="fw-bold text-primary">[INFO] User Service - 12:15:42</div>
                  <div>User registered: user_id=4</div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Layout>
  );
};

export default AdminDashboard; 