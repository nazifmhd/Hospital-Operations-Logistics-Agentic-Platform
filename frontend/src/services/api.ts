import axios from 'axios'
import toast from 'react-hot-toast'

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common error cases
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail)
    } else {
      toast.error('An unexpected error occurred')
    }
    
    return Promise.reject(error)
  }
)

// Bed Management API
export const bedApi = {
  // Get all beds
  getBeds: async () => {
    const response = await api.get('/beds')
    return response.data
  },

  // Get bed by ID
  getBed: async (id: string) => {
    const response = await api.get(`/beds/${id}`)
    return response.data
  },

  // Create new bed
  createBed: async (bed: any) => {
    const response = await api.post('/beds', bed)
    return response.data
  },

  // Update bed
  updateBed: async (id: string, bed: any) => {
    const response = await api.put(`/beds/${id}`, bed)
    return response.data
  },

  // Delete bed
  deleteBed: async (id: string) => {
    const response = await api.delete(`/beds/${id}`)
    return response.data
  },

  // Get bed status summary
  getBedStatus: async () => {
    const response = await api.get('/beds/status')
    return response.data
  }
}

// Staff Management API
export const staffApi = {
  // Get all staff
  getStaff: async () => {
    const response = await api.get('/staff')
    return response.data
  },

  // Get staff by ID
  getStaffMember: async (id: string) => {
    const response = await api.get(`/staff/${id}`)
    return response.data
  },

  // Create new staff member
  createStaff: async (staff: any) => {
    const response = await api.post('/staff', staff)
    return response.data
  },

  // Update staff member
  updateStaff: async (id: string, staff: any) => {
    const response = await api.put(`/staff/${id}`, staff)
    return response.data
  },

  // Delete staff member
  deleteStaff: async (id: string) => {
    const response = await api.delete(`/staff/${id}`)
    return response.data
  }
}

// Supply Management API
export const supplyApi = {
  // Get all supplies
  getSupplies: async () => {
    const response = await api.get('/supplies')
    return response.data
  },

  // Get supply by ID
  getSupply: async (id: string) => {
    const response = await api.get(`/supplies/${id}`)
    return response.data
  },

  // Create new supply
  createSupply: async (supply: any) => {
    const response = await api.post('/supplies', supply)
    return response.data
  },

  // Update supply
  updateSupply: async (id: string, supply: any) => {
    const response = await api.put(`/supplies/${id}`, supply)
    return response.data
  },

  // Delete supply
  deleteSupply: async (id: string) => {
    const response = await api.delete(`/supplies/${id}`)
    return response.data
  }
}

// Equipment Management API
export const equipmentApi = {
  // Get all equipment
  getEquipment: async () => {
    const response = await api.get('/equipment')
    return response.data
  },

  // Get equipment by ID
  getEquipmentItem: async (id: string) => {
    const response = await api.get(`/equipment/${id}`)
    return response.data
  },

  // Create new equipment
  createEquipment: async (equipment: any) => {
    const response = await api.post('/equipment', equipment)
    return response.data
  },

  // Update equipment
  updateEquipment: async (id: string, equipment: any) => {
    const response = await api.put(`/equipment/${id}`, equipment)
    return response.data
  },

  // Delete equipment
  deleteEquipment: async (id: string) => {
    const response = await api.delete(`/equipment/${id}`)
    return response.data
  }
}

export default api
