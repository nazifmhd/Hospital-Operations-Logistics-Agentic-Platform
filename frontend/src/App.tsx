import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import { Toaster } from 'react-hot-toast'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import BedsPage from './pages/Beds'
import EquipmentPage from './pages/Equipment'
import StaffPage from './pages/Staff'
import SuppliesPage from './pages/Supplies'
import AnalyticsPage from './pages/Analytics'

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/beds" element={<BedsPage />} />
          <Route path="/equipment" element={<EquipmentPage />} />
          <Route path="/staff" element={<StaffPage />} />
          <Route path="/supplies" element={<SuppliesPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Routes>
      </Layout>
      <Toaster position="top-right" />
    </Box>
  )
}

export default App
