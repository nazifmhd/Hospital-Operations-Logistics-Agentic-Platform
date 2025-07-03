import React from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  CircularProgress,
} from '@mui/material'
import {
  LocalHospital,
  Engineering,
  People,
  Inventory,
} from '@mui/icons-material'

// Mock data for demonstration
const mockDashboardData = {
  beds: {
    total: 150,
    available: 23,
    occupied: 127,
    occupancy_rate: 84.7
  },
  equipment: {
    total: 250,
    available: 180,
    in_use: 60,
    utilization: 72.5
  },
  staff: {
    total: 320,
    available: 280,
    on_duty: 240,
    utilization: 85.3
  },
  supplies: {
    total_items: 450,
    low_stock: 12,
    out_of_stock: 3,
    alerts: 8
  }
}

interface MetricCardProps {
  title: string
  value: number | string
  subtitle: string
  icon: React.ReactNode
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle, icon, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h3" component="div" color={`${color}.main`}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>
        <Box color={`${color}.main`}>
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
)

const Dashboard: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Hospital Operations Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Bed Management */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Bed Occupancy"
            value={`${mockDashboardData.beds.occupancy_rate}%`}
            subtitle={`${mockDashboardData.beds.occupied}/${mockDashboardData.beds.total} beds occupied`}
            icon={<LocalHospital sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>

        {/* Equipment Tracking */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Equipment Utilization"
            value={`${mockDashboardData.equipment.utilization}%`}
            subtitle={`${mockDashboardData.equipment.in_use}/${mockDashboardData.equipment.total} in use`}
            icon={<Engineering sx={{ fontSize: 40 }} />}
            color="secondary"
          />
        </Grid>

        {/* Staff Allocation */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Staff Utilization"
            value={`${mockDashboardData.staff.utilization}%`}
            subtitle={`${mockDashboardData.staff.on_duty}/${mockDashboardData.staff.total} on duty`}
            icon={<People sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>

        {/* Supply Inventory */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Supply Alerts"
            value={mockDashboardData.supplies.alerts}
            subtitle={`${mockDashboardData.supplies.low_stock} low stock items`}
            icon={<Inventory sx={{ fontSize: 40 }} />}
            color={mockDashboardData.supplies.alerts > 5 ? "warning" : "success"}
          />
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Box>
                <Paper sx={{ p: 2, mb: 1, backgroundColor: 'grey.50' }}>
                  <Typography variant="body2">
                    Bed 205 in ICU Unit cleaned and ready for next patient
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    2 minutes ago
                  </Typography>
                </Paper>
                <Paper sx={{ p: 2, mb: 1, backgroundColor: 'grey.50' }}>
                  <Typography variant="body2">
                    IV Pump EQ_001 moved to Emergency Room
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    5 minutes ago
                  </Typography>
                </Paper>
                <Paper sx={{ p: 2, mb: 1, backgroundColor: 'grey.50' }}>
                  <Typography variant="body2">
                    Dr. Sarah Johnson assigned to Surgery Unit
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    8 minutes ago
                  </Typography>
                </Paper>
                <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                  <Typography variant="body2">
                    Surgical gloves restocked in Supply Room A
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    12 minutes ago
                  </Typography>
                </Paper>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Agent Orchestrator</Typography>
                  <Box display="flex" alignItems="center">
                    <Box 
                      sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        backgroundColor: 'success.main',
                        mr: 1 
                      }} 
                    />
                    <Typography variant="body2" color="success.main">Online</Typography>
                  </Box>
                </Box>
                
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Bed Management Agent</Typography>
                  <Box display="flex" alignItems="center">
                    <Box 
                      sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        backgroundColor: 'success.main',
                        mr: 1 
                      }} 
                    />
                    <Typography variant="body2" color="success.main">Active</Typography>
                  </Box>
                </Box>
                
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Equipment Tracker Agent</Typography>
                  <Box display="flex" alignItems="center">
                    <Box 
                      sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        backgroundColor: 'success.main',
                        mr: 1 
                      }} 
                    />
                    <Typography variant="body2" color="success.main">Active</Typography>
                  </Box>
                </Box>
                
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Typography variant="body2">Staff Allocation Agent</Typography>
                  <Box display="flex" alignItems="center">
                    <Box 
                      sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        backgroundColor: 'success.main',
                        mr: 1 
                      }} 
                    />
                    <Typography variant="body2" color="success.main">Active</Typography>
                  </Box>
                </Box>
                
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2">Supply Inventory Agent</Typography>
                  <Box display="flex" alignItems="center">
                    <Box 
                      sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        backgroundColor: 'success.main',
                        mr: 1 
                      }} 
                    />
                    <Typography variant="body2" color="success.main">Active</Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
