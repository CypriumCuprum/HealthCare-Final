# Healthcare System Frontend

This is the React frontend for the Healthcare Microservices System. It provides interfaces for different user roles including patients, doctors, pharmacists, and administrators.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Backend API URLs**:
   - Open `src/services/api.js` and update the service URLs if needed:
     ```javascript
     const USER_SERVICE_URL = 'http://localhost:8000/api/v1';
     const PHARMACY_SERVICE_URL = 'http://localhost:8081/api/v1';
     ```

3. **Start Development Server**:
   ```bash
   npm start
   ```

4. **Build for Production**:
   ```bash
   npm run build
   ```

## Authentication

For development purposes, the frontend uses hardcoded tokens that match the backend service's token map:

- Patient: `patient_token`
- Doctor: `doctor_token`
- Pharmacist: `admin_token` (using admin token for pharmacist role in development)
- Admin: `admin_token`
- Default: `dev_token_123456`

In the login page, you can select your role and the system will use the appropriate token.

## Features

### Patient Features
- View dashboard with healthcare overview
- Browse and view prescription history and details
- View medication details and dispensing history

### Doctor Features
- Create new prescriptions for patients
- View prescriptions history for patients

### Pharmacist Features
- Dashboard with pending prescriptions and inventory status
- Verify prescriptions
- Dispense medications
- Manage pharmacy inventory

### Admin Features
- Manage medication catalog
- System configuration

## Project Structure

- `src/contexts/AuthContext.js`: Authentication state management
- `src/services/api.js`: API service for backend communication
- `src/components/`: Reusable UI components
- `src/pages/`: Role-specific page components
  - `patient/`: Patient-facing pages
  - `doctor/`: Doctor-facing pages
  - `pharmacist/`: Pharmacist-facing pages
  - `admin/`: Admin-facing pages

## API Integration

The frontend is designed to work with the following backend services:

- User Service (port 8000): Handles authentication and user management
- Pharmacy Service (port 8081): Handles prescriptions and medication management

## Development Notes

- In development mode, if the backend APIs are unavailable, the frontend will use mock data
- All API calls include the authentication token in the request headers
- Role-based access control is implemented both on the frontend (routes) and backend 