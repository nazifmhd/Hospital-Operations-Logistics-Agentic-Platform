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
  Avatar
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, Person as PersonIcon } from '@mui/icons-material'
import { staffApi } from '../services/api'
import { Staff } from '../types'

const StaffPage: React.FC = () => {
  const [staff, setStaff] = useState<Staff[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [editingStaff, setEditingStaff] = useState<Staff | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    role: 'nurse',
    department: '',
    status: 'off_duty',
    email: '',
    phone: '',
    license_number: '',
    experience_years: 0,
    hourly_rate: 0
  })

  useEffect(() => {
    fetchStaff()
  }, [])

  const fetchStaff = async () => {
    try {
      setLoading(true)
      const data = await staffApi.getStaff()
      setStaff(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch staff')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenDialog = (staffMember?: Staff) => {
    if (staffMember) {
      setEditingStaff(staffMember)
      setFormData({
        name: staffMember.name,
        role: staffMember.role,
        department: staffMember.department,
        status: staffMember.status,
        email: staffMember.email || '',
        phone: staffMember.phone || '',
        license_number: staffMember.license_number || '',
        experience_years: staffMember.experience_years || 0,
        hourly_rate: staffMember.hourly_rate || 0
      })
    } else {
      setEditingStaff(null)
      setFormData({
        name: '',
        role: 'nurse',
        department: '',
        status: 'off_duty',
        email: '',
        phone: '',
        license_number: '',
        experience_years: 0,
        hourly_rate: 0
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingStaff(null)
  }

  const handleSubmit = async () => {
    try {
      if (editingStaff) {
        await staffApi.updateStaff(editingStaff.id, formData)
      } else {
        await staffApi.createStaff(formData)
      }
      handleCloseDialog()
      fetchStaff()
    } catch (err: any) {
      setError(err.message || 'Failed to save staff member')
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this staff member?')) {
      try {
        await staffApi.deleteStaff(id)
        fetchStaff()
      } catch (err: any) {
        setError(err.message || 'Failed to delete staff member')
      }
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'doctor': return 'error'
      case 'nurse': return 'primary'
      case 'specialist': return 'secondary'
      case 'technician': return 'info'
      case 'therapist': return 'success'
      case 'administrator': return 'warning'
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
          Staff Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Staff Member
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
                Total Staff
              </Typography>
              <Typography variant="h4">
                {staff.length}
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
                {staff.filter(s => s.status === 'available').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                On Duty
              </Typography>
              <Typography variant="h4" color="warning.main">
                {staff.filter(s => s.status === 'on_duty').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Experience Avg.
              </Typography>
              <Typography variant="h4">
                {staff.length > 0 ? Math.round(staff.reduce((sum, s) => sum + (s.experience_years || 0), 0) / staff.length) : 0} yrs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Staff Directory
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Staff</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Experience</TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {staff.map((staffMember) => (
                  <TableRow key={staffMember.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar sx={{ mr: 2 }}>
                          <PersonIcon />
                        </Avatar>
                        {staffMember.name}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={staffMember.role.toUpperCase()}
                        color={getRoleColor(staffMember.role) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{staffMember.department}</TableCell>
                    <TableCell>
                      <Chip
                        label={staffMember.status.replace('_', ' ').toUpperCase()}
                        color={staffMember.status === 'available' ? 'success' : staffMember.status === 'on_duty' ? 'warning' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{staffMember.experience_years || 0} years</TableCell>
                    <TableCell>{staffMember.email || '-'}</TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenDialog(staffMember)}
                        sx={{ mr: 1 }}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={() => handleDelete(staffMember.id)}
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
          {editingStaff ? 'Edit Staff Member' : 'Add New Staff Member'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Role</InputLabel>
                  <Select
                    value={formData.role}
                    label="Role"
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  >
                    <MenuItem value="nurse">Nurse</MenuItem>
                    <MenuItem value="doctor">Doctor</MenuItem>
                    <MenuItem value="specialist">Specialist</MenuItem>
                    <MenuItem value="technician">Technician</MenuItem>
                    <MenuItem value="therapist">Therapist</MenuItem>
                    <MenuItem value="administrator">Administrator</MenuItem>
                    <MenuItem value="support">Support</MenuItem>
                  </Select>
                </FormControl>
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
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    label="Status"
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  >
                    <MenuItem value="available">Available</MenuItem>
                    <MenuItem value="on_duty">On Duty</MenuItem>
                    <MenuItem value="off_duty">Off Duty</MenuItem>
                    <MenuItem value="on_break">On Break</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="License Number"
                  value={formData.license_number}
                  onChange={(e) => setFormData({ ...formData, license_number: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Experience (Years)"
                  type="number"
                  value={formData.experience_years}
                  onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) || 0 })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Hourly Rate"
                  type="number"
                  value={formData.hourly_rate}
                  onChange={(e) => setFormData({ ...formData, hourly_rate: parseFloat(e.target.value) || 0 })}
                  inputProps={{ step: "0.01" }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingStaff ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default StaffPage
