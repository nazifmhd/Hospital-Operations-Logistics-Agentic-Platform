import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Alert
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { bedApi } from '../services/api'
import { Bed } from '../types'

const BedsPage: React.FC = () => {
  const [beds, setBeds] = useState<Bed[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [editingBed, setEditingBed] = useState<Bed | null>(null)
  const [formData, setFormData] = useState({
    room_number: '',
    department: '',
    bed_type: 'general',
    status: 'available'
  })

  useEffect(() => {
    fetchBeds()
  }, [])

  const fetchBeds = async () => {
    try {
      setLoading(true)
      const data = await bedApi.getBeds()
      setBeds(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch beds')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenDialog = (bed?: Bed) => {
    if (bed) {
      setEditingBed(bed)
      setFormData({
        room_number: bed.room_number,
        department: bed.department,
        bed_type: bed.bed_type,
        status: bed.status
      })
    } else {
      setEditingBed(null)
      setFormData({
        room_number: '',
        department: '',
        bed_type: 'general',
        status: 'available'
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingBed(null)
  }

  const handleSubmit = async () => {
    try {
      if (editingBed) {
        await bedApi.updateBed(editingBed.id, formData)
      } else {
        await bedApi.createBed(formData)
      }
      handleCloseDialog()
      fetchBeds()
    } catch (err: any) {
      setError(err.message || 'Failed to save bed')
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this bed?')) {
      try {
        await bedApi.deleteBed(id)
        fetchBeds()
      } catch (err: any) {
        setError(err.message || 'Failed to delete bed')
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'success'
      case 'occupied': return 'warning'
      case 'maintenance': return 'error'
      case 'cleaning': return 'info'
      default: return 'default'
    }
  }

  const getBedTypeColor = (type: string) => {
    switch (type) {
      case 'ICU': return 'error'
      case 'general': return 'primary'
      case 'emergency': return 'warning'
      case 'surgery': return 'secondary'
      case 'maternity': return 'success'
      default: return 'default'
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Bed Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Bed
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Beds
              </Typography>
              <Typography variant="h4">
                {beds.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Available
              </Typography>
              <Typography variant="h4" color="success.main">
                {beds.filter(bed => bed.status === 'available').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Occupied
              </Typography>
              <Typography variant="h4" color="warning.main">
                {beds.filter(bed => bed.status === 'occupied').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Occupancy Rate
              </Typography>
              <Typography variant="h4">
                {beds.length > 0 ? Math.round((beds.filter(bed => bed.status === 'occupied').length / beds.length) * 100) : 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Bed Status Overview
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Room Number</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Bed Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Patient ID</TableCell>
                  <TableCell>Last Updated</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {beds.map((bed) => (
                  <TableRow key={bed.id}>
                    <TableCell>{bed.room_number}</TableCell>
                    <TableCell>{bed.department}</TableCell>
                    <TableCell>
                      <Chip
                        label={bed.bed_type.toUpperCase()}
                        color={getBedTypeColor(bed.bed_type) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={bed.status.toUpperCase()}
                        color={getStatusColor(bed.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{bed.patient_id || '-'}</TableCell>
                    <TableCell>
                      {new Date(bed.updated_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenDialog(bed)}
                        sx={{ mr: 1 }}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={() => handleDelete(bed.id)}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingBed ? 'Edit Bed' : 'Add New Bed'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Room Number"
                  value={formData.room_number}
                  onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Department"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Bed Type</InputLabel>
                  <Select
                    value={formData.bed_type}
                    label="Bed Type"
                    onChange={(e) => setFormData({ ...formData, bed_type: e.target.value })}
                  >
                    <MenuItem value="general">General</MenuItem>
                    <MenuItem value="ICU">ICU</MenuItem>
                    <MenuItem value="emergency">Emergency</MenuItem>
                    <MenuItem value="surgery">Surgery</MenuItem>
                    <MenuItem value="maternity">Maternity</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    label="Status"
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  >
                    <MenuItem value="available">Available</MenuItem>
                    <MenuItem value="occupied">Occupied</MenuItem>
                    <MenuItem value="maintenance">Maintenance</MenuItem>
                    <MenuItem value="cleaning">Cleaning</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingBed ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default BedsPage
