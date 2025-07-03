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
  Alert,
  LinearProgress
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, Build as BuildIcon } from '@mui/icons-material'
import { equipmentApi } from '../services/api'
import { Equipment } from '../types'

const EquipmentPage: React.FC = () => {
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [editingEquipment, setEditingEquipment] = useState<Equipment | null>(null)
  const [formData, setFormData] = useState({
    asset_id: '',
    name: '',
    equipment_type: '',
    model: '',
    manufacturer: '',
    status: 'available',
    building: '',
    floor: '',
    unit: '',
    room: ''
  })

  useEffect(() => {
    fetchEquipment()
  }, [])

  const fetchEquipment = async () => {
    try {
      setLoading(true)
      const data = await equipmentApi.getEquipment()
      setEquipment(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch equipment')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenDialog = (equipmentItem?: Equipment) => {
    if (equipmentItem) {
      setEditingEquipment(equipmentItem)
      setFormData({
        asset_id: equipmentItem.asset_id,
        name: equipmentItem.name,
        equipment_type: equipmentItem.equipment_type,
        model: equipmentItem.model || '',
        manufacturer: equipmentItem.manufacturer || '',
        status: equipmentItem.status,
        building: equipmentItem.location?.building || '',
        floor: equipmentItem.location?.floor || '',
        unit: equipmentItem.location?.unit || '',
        room: equipmentItem.location?.room || ''
      })
    } else {
      setEditingEquipment(null)
      setFormData({
        asset_id: '',
        name: '',
        equipment_type: '',
        model: '',
        manufacturer: '',
        status: 'available',
        building: '',
        floor: '',
        unit: '',
        room: ''
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingEquipment(null)
  }

  const handleSubmit = async () => {
    try {
      const equipmentData = {
        ...formData,
        location: {
          building: formData.building,
          floor: formData.floor,
          unit: formData.unit,
          room: formData.room
        }
      }
      
      if (editingEquipment) {
        await equipmentApi.updateEquipment(editingEquipment.asset_id, equipmentData)
      } else {
        await equipmentApi.createEquipment(equipmentData)
      }
      handleCloseDialog()
      fetchEquipment()
    } catch (err: any) {
      setError(err.message || 'Failed to save equipment')
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this equipment?')) {
      try {
        await equipmentApi.deleteEquipment(id)
        fetchEquipment()
      } catch (err: any) {
        setError(err.message || 'Failed to delete equipment')
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'success'
      case 'in_use': return 'warning'
      case 'maintenance': return 'info'
      case 'out_of_order': return 'error'
      case 'reserved': return 'secondary'
      default: return 'default'
    }
  }

  const getConditionColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'error'
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
          Equipment Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Equipment
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
                Total Equipment
              </Typography>
              <Typography variant="h4">
                {equipment.length}
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
                {equipment.filter(eq => eq.status === 'available').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                In Use
              </Typography>
              <Typography variant="h4" color="warning.main">
                {equipment.filter(eq => eq.status === 'in_use').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Need Maintenance
              </Typography>
              <Typography variant="h4" color="error.main">
                {equipment.filter(eq => eq.status === 'maintenance' || eq.status === 'out_of_order').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Equipment Inventory
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Asset ID</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Condition</TableCell>
                  <TableCell>Usage Hours</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {equipment.map((item) => (
                  <TableRow key={item.asset_id}>
                    <TableCell>{item.asset_id}</TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <BuildIcon sx={{ mr: 1, color: 'text.secondary' }} />
                        {item.name}
                      </Box>
                    </TableCell>
                    <TableCell>{item.equipment_type}</TableCell>
                    <TableCell>
                      <Chip
                        label={item.status.replace('_', ' ').toUpperCase()}
                        color={getStatusColor(item.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {item.location?.room ? 
                        `${item.location.building || ''} ${item.location.floor || ''} ${item.location.unit || ''} ${item.location.room}`.trim() 
                        : '-'
                      }
                    </TableCell>
                    <TableCell>
                      <Box>
                        <LinearProgress
                          variant="determinate"
                          value={item.condition_score}
                          color={getConditionColor(item.condition_score)}
                          sx={{ mb: 0.5 }}
                        />
                        <Typography variant="caption">
                          {item.condition_score}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{item.usage_hours.toLocaleString()}h</TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenDialog(item)}
                        sx={{ mr: 1 }}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={() => handleDelete(item.asset_id)}
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
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingEquipment ? 'Edit Equipment' : 'Add New Equipment'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Asset ID"
                  value={formData.asset_id}
                  onChange={(e) => setFormData({ ...formData, asset_id: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Equipment Type"
                  value={formData.equipment_type}
                  onChange={(e) => setFormData({ ...formData, equipment_type: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    label="Status"
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  >
                    <MenuItem value="available">Available</MenuItem>
                    <MenuItem value="in_use">In Use</MenuItem>
                    <MenuItem value="maintenance">Maintenance</MenuItem>
                    <MenuItem value="out_of_order">Out of Order</MenuItem>
                    <MenuItem value="reserved">Reserved</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Model"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Manufacturer"
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Location</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Building"
                  value={formData.building}
                  onChange={(e) => setFormData({ ...formData, building: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Floor"
                  value={formData.floor}
                  onChange={(e) => setFormData({ ...formData, floor: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Unit"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Room"
                  value={formData.room}
                  onChange={(e) => setFormData({ ...formData, room: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingEquipment ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default EquipmentPage
