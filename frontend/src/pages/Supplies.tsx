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
  CircularProgress,
  Alert,
  LinearProgress
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, Inventory as InventoryIcon, Warning as WarningIcon } from '@mui/icons-material'
import { supplyApi } from '../services/api'
import { Supply } from '../types'

const SuppliesPage: React.FC = () => {
  const [supplies, setSupplies] = useState<Supply[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [editingSupply, setEditingSupply] = useState<Supply | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    current_stock: 0,
    minimum_threshold: 0,
    maximum_capacity: 0,
    unit_cost: 0,
    supplier: '',
    location: ''
  })

  useEffect(() => {
    fetchSupplies()
  }, [])

  const fetchSupplies = async () => {
    try {
      setLoading(true)
      const data = await supplyApi.getSupplies()
      setSupplies(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch supplies')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenDialog = (supply?: Supply) => {
    if (supply) {
      setEditingSupply(supply)
      setFormData({
        name: supply.name,
        category: supply.category,
        current_stock: supply.current_stock,
        minimum_threshold: supply.minimum_threshold,
        maximum_capacity: supply.maximum_capacity,
        unit_cost: supply.unit_cost,
        supplier: supply.supplier || '',
        location: supply.location
      })
    } else {
      setEditingSupply(null)
      setFormData({
        name: '',
        category: '',
        current_stock: 0,
        minimum_threshold: 0,
        maximum_capacity: 0,
        unit_cost: 0,
        supplier: '',
        location: ''
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingSupply(null)
  }

  const handleSubmit = async () => {
    try {
      if (editingSupply) {
        await supplyApi.updateSupply(editingSupply.id, formData)
      } else {
        await supplyApi.createSupply(formData)
      }
      handleCloseDialog()
      fetchSupplies()
    } catch (err: any) {
      setError(err.message || 'Failed to save supply')
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this supply item?')) {
      try {
        await supplyApi.deleteSupply(id)
        fetchSupplies()
      } catch (err: any) {
        setError(err.message || 'Failed to delete supply')
      }
    }
  }

  const getStockStatus = (supply: Supply) => {
    if (supply.current_stock <= supply.minimum_threshold) return { status: 'critical', color: 'error', label: 'CRITICAL' }
    if (supply.current_stock <= supply.minimum_threshold * 1.5) return { status: 'low', color: 'warning', label: 'LOW' }
    if (supply.current_stock >= supply.maximum_capacity) return { status: 'overstocked', color: 'info', label: 'OVERSTOCKED' }
    return { status: 'normal', color: 'success', label: 'NORMAL' }
  }

  const getStockPercentage = (supply: Supply) => {
    return Math.min((supply.current_stock / supply.maximum_capacity) * 100, 100)
  }

  const lowStockCount = supplies.filter(s => s.current_stock <= s.minimum_threshold).length
  const totalValue = supplies.reduce((sum, s) => sum + (s.current_stock * s.unit_cost), 0)

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
          Supply Inventory
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Supply Item
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
                Total Items
              </Typography>
              <Typography variant="h4">
                {supplies.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Low Stock Items
              </Typography>
              <Typography variant="h4" color="error.main">
                {lowStockCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Value
              </Typography>
              <Typography variant="h4" color="success.main">
                ${totalValue.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Categories
              </Typography>
              <Typography variant="h4">
                {new Set(supplies.map(s => s.category)).size}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Inventory Overview
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Item ID</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Stock Level</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Unit Cost</TableCell>
                  <TableCell>Total Value</TableCell>
                  <TableCell>Supplier</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {supplies.map((supply) => {
                  const stockStatus = getStockStatus(supply)
                  return (
                    <TableRow key={supply.id}>
                      <TableCell>{supply.id}</TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <InventoryIcon sx={{ mr: 1, color: 'text.secondary' }} />
                          {supply.name}
                        </Box>
                      </TableCell>
                      <TableCell>{supply.category}</TableCell>
                      <TableCell>
                        <Box>
                          <Box display="flex" alignItems="center" mb={0.5}>
                            <Typography variant="body2" sx={{ mr: 1 }}>
                              {supply.current_stock} / {supply.maximum_capacity}
                            </Typography>
                            {stockStatus.status === 'critical' && (
                              <WarningIcon color="error" fontSize="small" />
                            )}
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={getStockPercentage(supply)}
                            color={stockStatus.color as any}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={stockStatus.label}
                          color={stockStatus.color as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>${supply.unit_cost.toFixed(2)}</TableCell>
                      <TableCell>${(supply.current_stock * supply.unit_cost).toFixed(2)}</TableCell>
                      <TableCell>{supply.supplier || '-'}</TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<EditIcon />}
                          onClick={() => handleOpenDialog(supply)}
                          sx={{ mr: 1 }}
                        >
                          Edit
                        </Button>
                        <Button
                          size="small"
                          color="error"
                          startIcon={<DeleteIcon />}
                          onClick={() => handleDelete(supply.id)}
                        >
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingSupply ? 'Edit Supply Item' : 'Add New Supply Item'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
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
                  label="Category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Current Stock"
                  type="number"
                  value={formData.current_stock}
                  onChange={(e) => setFormData({ ...formData, current_stock: parseInt(e.target.value) || 0 })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Minimum Threshold"
                  type="number"
                  value={formData.minimum_threshold}
                  onChange={(e) => setFormData({ ...formData, minimum_threshold: parseInt(e.target.value) || 0 })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Maximum Capacity"
                  type="number"
                  value={formData.maximum_capacity}
                  onChange={(e) => setFormData({ ...formData, maximum_capacity: parseInt(e.target.value) || 0 })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Unit Cost"
                  type="number"
                  value={formData.unit_cost}
                  onChange={(e) => setFormData({ ...formData, unit_cost: parseFloat(e.target.value) || 0 })}
                  inputProps={{ step: "0.01" }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Supplier"
                  value={formData.supplier}
                  onChange={(e) => setFormData({ ...formData, supplier: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Location"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingSupply ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default SuppliesPage
