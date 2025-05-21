import React from 'react';
import { Container, Navbar, Nav, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Layout = ({ children }) => {
  const { currentUser, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Get navigation links based on user role
  const getNavLinks = () => {
    switch (role) {
      case 'PATIENT':
        return (
          <>
            <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/patient/prescriptions">My Prescriptions</Nav.Link>
          </>
        );
      case 'DOCTOR':
        return (
          <>
            <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/doctor/prescriptions">Prescriptions</Nav.Link>
            <Nav.Link as={Link} to="/doctor/prescriptions/new">Create Prescription</Nav.Link>
          </>
        );
      case 'PHARMACIST':
        return (
          <>
            <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/pharmacist/prescriptions/pending">Pending Prescriptions</Nav.Link>
            <Nav.Link as={Link} to="/pharmacist/stock">Inventory</Nav.Link>
          </>
        );
      case 'ADMIN':
        return (
          <>
            <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/admin/medications">Medication Catalog</Nav.Link>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <>
      <Navbar bg="primary" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand as={Link} to="/">Healthcare System</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              {getNavLinks()}
            </Nav>
            <Nav>
              {currentUser ? (
                <div className="d-flex align-items-center">
                  <span className="text-white me-3">
                    Hello, {currentUser.first_name} ({role})
                  </span>
                  <Button variant="outline-light" onClick={handleLogout}>
                    Logout
                  </Button>
                </div>
              ) : (
                <>
                  <Nav.Link as={Link} to="/login">Login</Nav.Link>
                  <Nav.Link as={Link} to="/register">Register</Nav.Link>
                </>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="py-3">
        {children}
      </Container>

      <footer className="bg-light py-3 mt-5">
        <Container>
          <p className="text-center text-muted mb-0">
            &copy; {new Date().getFullYear()} Healthcare System
          </p>
        </Container>
      </footer>
    </>
  );
};

export default Layout; 