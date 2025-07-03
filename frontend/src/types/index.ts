// Common types used across the application

export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
}

// Bed Management Types
export interface Bed {
  id: string
  room_number: string
  department: string
  bed_type: string
  status: string
  patient_id?: string
  last_cleaned?: string
  created_at: string
  updated_at: string
  floor?: string
  wing?: string
  isolation_required?: boolean
  special_equipment?: string
}

export interface BedStatusSummary {
  total_beds: number
  available: number
  occupied: number
  maintenance: number
  cleaning: number
  occupancy_rate: number
  turnover_rate: number
  average_length_of_stay: number
}

// Equipment Types
export interface Equipment {
  asset_id: string
  name: string
  equipment_type: string
  model?: string
  manufacturer?: string
  status: 'available' | 'in_use' | 'maintenance' | 'out_of_order' | 'reserved'
  location: {
    building?: string
    floor?: string
    unit?: string
    room?: string
  }
  condition_score: number
  usage_hours: number
  last_maintenance?: string
  next_maintenance_due?: string
  created_at: string
  updated_at: string
}

export interface EquipmentStatusSummary {
  total_equipment: number
  available: number
  in_use: number
  in_maintenance: number
  out_of_order: number
  average_utilization: number
  tracking_accuracy: number
  maintenance_compliance: number
}

// Staff Types
export interface Staff {
  id: string
  name: string
  role: string
  department: string
  status: string
  email?: string
  phone?: string
  shift_start?: string
  shift_end?: string
  created_at: string
  updated_at: string
  license_number?: string
  experience_years?: number
  specializations?: string
  hourly_rate?: number
}

export interface StaffStatusSummary {
  total_staff: number
  available_staff: number
  active_assignments: number
  average_workload: number
  staff_by_department: Record<string, number>
  workload_alerts: number
}

// Supply Types
export interface Supply {
  id: string
  name: string
  category: string
  current_stock: number
  minimum_threshold: number
  maximum_capacity: number
  unit_cost: number
  supplier?: string
  location: string
  expiry_date?: string
  status: string
  created_at: string
  updated_at: string
  batch_number?: string
  manufacturer?: string
  storage_requirements?: string
}

export interface SupplyStatusSummary {
  total_items: number
  low_stock_items: number
  out_of_stock_items: number
  expired_items: number
  total_inventory_value: number
  active_orders: number
  alerts_count: number
  categories: Record<string, number>
}

// Analytics Types
export interface UtilizationMetrics {
  bed_utilization: number
  equipment_utilization: number
  staff_utilization: number
  supply_turnover: number
  efficiency_score: number
}

export interface TrendData {
  date: string
  value: number
  category?: string
}

export interface AlertItem {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  timestamp: string
  resolved: boolean
  severity: 'low' | 'medium' | 'high' | 'critical'
}

export interface DashboardData {
  summary: {
    beds: BedStatusSummary
    equipment: EquipmentStatusSummary
    staff: StaffStatusSummary
    supplies: SupplyStatusSummary
  }
  utilization_metrics: UtilizationMetrics
  recent_alerts: AlertItem[]
  trends: {
    occupancy: TrendData[]
    utilization: TrendData[]
    efficiency: TrendData[]
  }
}
