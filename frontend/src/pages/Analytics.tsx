import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material'
import {
  Hotel,
  People,
  Build,
  Warning,
  CheckCircle
} from '@mui/icons-material'
import { bedApi, staffApi, equipmentApi, supplyApi } from '../services/api'

interface AnalyticsData {
  beds: any[]
  staff: any[]
  equipment: any[]
  supplies: any[]
}

const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsData>({ beds: [], staff: [], equipment: [], supplies: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAnalyticsData()
  }, [])

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true)
      const [beds, staff, equipment, supplies] = await Promise.all([
        bedApi.getBeds(),
        staffApi.getStaff(),
        equipmentApi.getEquipment(),
        supplyApi.getSupplies()
      ])
      setData({ beds, staff, equipment, supplies })
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch analytics data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
        <CircularProgress />
      </Box>
    )
  }

  // Calculate metrics
  const bedMetrics = {
    total: data.beds.length,
    occupied: data.beds.filter(b => b.status === 'occupied').length,
    available: data.beds.filter(b => b.status === 'available').length,
    maintenance: data.beds.filter(b => b.status === 'maintenance').length,
    occupancyRate: data.beds.length > 0 ? (data.beds.filter(b => b.status === 'occupied').length / data.beds.length * 100) : 0
  }

  const staffMetrics = {
    total: data.staff.length,
    available: data.staff.filter(s => s.is_available).length,
    busy: data.staff.filter(s => !s.is_available).length,
    avgWorkload: data.staff.length > 0 ? data.staff.reduce((sum, s) => sum + s.current_patient_load, 0) / data.staff.length : 0
  }

  const equipmentMetrics = {
    total: data.equipment.length,
    available: data.equipment.filter(e => e.status === 'available').length,
    inUse: data.equipment.filter(e => e.status === 'in_use').length,
    maintenance: data.equipment.filter(e => e.status === 'maintenance' || e.status === 'out_of_order').length,
    avgCondition: data.equipment.length > 0 ? data.equipment.reduce((sum, e) => sum + e.condition_score, 0) / data.equipment.length : 0
  }

  const supplyMetrics = {
    total: data.supplies.length,
    lowStock: data.supplies.filter(s => s.current_stock <= s.min_stock_level).length,
    totalValue: data.supplies.reduce((sum, s) => sum + (s.current_stock * s.unit_cost), 0),
    categories: new Set(data.supplies.map(s => s.category)).size
  }

  const departmentStats = data.beds.reduce((acc, bed) => {
    if (!acc[bed.department]) {
      acc[bed.department] = { total: 0, occupied: 0, available: 0 }
    }
    acc[bed.department].total++
    if (bed.status === 'occupied') acc[bed.department].occupied++
    if (bed.status === 'available') acc[bed.department].available++
    return acc
  }, {} as Record<string, any>)

  const roleStats = data.staff.reduce((acc, staff) => {
    if (!acc[staff.role]) {
      acc[staff.role] = { total: 0, available: 0, busy: 0 }
    }
    acc[staff.role].total++
    if (staff.is_available) acc[staff.role].available++
    else acc[staff.role].busy++
    return acc
  }, {} as Record<string, any>)

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics & Reports
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Key Performance Indicators */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Bed Occupancy Rate
                  </Typography>
                  <Typography variant="h4" color={bedMetrics.occupancyRate > 80 ? 'error.main' : 'success.main'}>
                    {bedMetrics.occupancyRate.toFixed(1)}%
                  </Typography>
                </Box>
                <Hotel color={bedMetrics.occupancyRate > 80 ? 'error' : 'success'} fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Staff Availability
                  </Typography>
                  <Typography variant="h4" color="primary.main">
                    {staffMetrics.available}/{staffMetrics.total}
                  </Typography>
                </Box>
                <People color="primary" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Equipment Condition
                  </Typography>
                  <Typography variant="h4" color={equipmentMetrics.avgCondition < 70 ? 'error.main' : 'success.main'}>
                    {equipmentMetrics.avgCondition.toFixed(1)}%
                  </Typography>
                </Box>
                <Build color={equipmentMetrics.avgCondition < 70 ? 'error' : 'success'} fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Low Stock Alerts
                  </Typography>
                  <Typography variant="h4" color={supplyMetrics.lowStock > 0 ? 'error.main' : 'success.main'}>
                    {supplyMetrics.lowStock}
                  </Typography>
                </Box>
                {supplyMetrics.lowStock > 0 ? (
                  <Warning color="error" fontSize="large" />
                ) : (
                  <CheckCircle color="success" fontSize="large" />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Bed Management Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Total Beds</Typography>
                  <Typography variant="h6">{bedMetrics.total}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Available</Typography>
                  <Typography variant="h6" color="success.main">{bedMetrics.available}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Occupied</Typography>
                  <Typography variant="h6" color="warning.main">{bedMetrics.occupied}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Maintenance</Typography>
                  <Typography variant="h6" color="error.main">{bedMetrics.maintenance}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Supply Inventory Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Total Items</Typography>
                  <Typography variant="h6">{supplyMetrics.total}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Categories</Typography>
                  <Typography variant="h6">{supplyMetrics.categories}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Total Value</Typography>
                  <Typography variant="h6" color="success.main">${supplyMetrics.totalValue.toLocaleString()}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Low Stock</Typography>
                  <Typography variant="h6" color="error.main">{supplyMetrics.lowStock}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Department Analysis */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Department Bed Utilization
              </Typography>
              <TableContainer component={Paper} elevation={0}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Department</TableCell>
                      <TableCell align="right">Total</TableCell>
                      <TableCell align="right">Occupied</TableCell>
                      <TableCell align="right">Rate</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(departmentStats).map(([dept, stats]: [string, any]) => (
                      <TableRow key={dept}>
                        <TableCell>{dept}</TableCell>
                        <TableCell align="right">{stats.total}</TableCell>
                        <TableCell align="right">{stats.occupied}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={`${((stats.occupied / stats.total) * 100).toFixed(1)}%`}
                            size="small"
                            color={(stats.occupied / stats.total) > 0.8 ? 'error' : 'success'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Staff Distribution by Role
              </Typography>
              <TableContainer component={Paper} elevation={0}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Role</TableCell>
                      <TableCell align="right">Total</TableCell>
                      <TableCell align="right">Available</TableCell>
                      <TableCell align="right">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(roleStats).map(([role, stats]: [string, any]) => (
                      <TableRow key={role}>
                        <TableCell sx={{ textTransform: 'capitalize' }}>{role}</TableCell>
                        <TableCell align="right">{stats.total}</TableCell>
                        <TableCell align="right">{stats.available}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={stats.available > 0 ? 'Available' : 'All Busy'}
                            size="small"
                            color={stats.available > 0 ? 'success' : 'warning'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default AnalyticsPage
