import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import PCDetail from './components/PCDetail';
import AuditLog from './components/AuditLog';
import AddPCModal from './components/AddPCModal';

function App() {
  return (
    <AppProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/node/:id" element={<PCDetail />} />
            <Route path="/audit" element={<AuditLog />} />
          </Routes>
          <AddPCModal />
        </Layout>
      </Router>
    </AppProvider>
  );
}

export default App;
