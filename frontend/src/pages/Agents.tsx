import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  LinearProgress,
  IconButton,
  Tooltip
} from '@mui/material'
import {
  Memory,
  Refresh,
  Info,
  Speed,
  CheckCircle,
  Error,
  Settings,
  PlayArrow,
  Pause
} from '@mui/icons-material'

interface AgentData {
  status: string
  agent_type: string
  last_activity: string
  message: string
  metrics?: {
    events_processed: number
    decisions_made: number
    errors_count: number
    average_response_time: number
  }
}

interface AgentStatus {
  agents: Record<string, AgentData>
  system_status: string
  total_agents: number
  active_agents: number
}

interface AgentEvent {
  timestamp: string
  agent_id: string
  event_type: string
  message: string
  severity: string
}

interface PerformanceMetrics {
  system_metrics: {
    uptime_hours: number
    messages_processed: number
    average_response_time: number
    error_rate: number
  }
  agent_metrics: Record<string, any>
}

const AgentsPage: React.FC = () => {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null)
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [debugInfo, setDebugInfo] = useState<string>('Starting...')

  const fetchAgentData = async () => {
    try {
      setLoading(true)
      setError(null)
      setDebugInfo('Fetching agent data...')

      console.log('Fetching agent data...')

      // Use direct backend URL
      const baseUrl = 'http://localhost:8000'
      
      setDebugInfo('Making fetch requests...')
      const statusResponse = await fetch(`${baseUrl}/api/v1/agents/`)
      
      setDebugInfo(`Status response: ${statusResponse.status}`)
      console.log('Status response:', statusResponse.status)

      if (!statusResponse.ok) throw new globalThis.Error(`Failed to fetch agent status: ${statusResponse.status}`)

      const statusData = await statusResponse.json()
      setDebugInfo(`Got status data: ${JSON.stringify(statusData).substring(0, 100)}...`)
      console.log('Agent status data:', statusData)

      setAgentStatus(statusData)
      setEvents([]) 
      setMetrics(null) 
      setDebugInfo('Data loaded successfully!')
    } catch (err) {
      console.error('Error fetching agent data:', err)
      setError(err instanceof globalThis.Error ? err.message : 'Failed to fetch agent data')
      setDebugInfo(`Error: ${err}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgentData()
    const interval = setInterval(fetchAgentData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running': return 'success'
      case 'error': return 'error'
      case 'paused': return 'warning'
      default: return 'default'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'error': return 'error'
      case 'warning': return 'warning'
      case 'info': return 'info'
      default: return 'default'
    }
  }

  const getAgentIcon = (agentType: string) => {
    switch (agentType.toLowerCase()) {
      case 'bedmanagementagent': return '🛏️'
      case 'equipmenttrackeragent': return '🔧'
      case 'staffallocationagent': return '👥'
      case 'supplyinventoryagent': return '📦'
      default: return '🤖'
    }
  }

  const getAgentDisplayName = (agentType: string) => {
    switch (agentType.toLowerCase()) {
      case 'bedmanagementagent': return 'Bed Management'
      case 'equipmenttrackeragent': return 'Equipment Tracker'
      case 'staffallocationagent': return 'Staff Allocation'
      case 'supplyinventoryagent': return 'Supply Inventory'
      default: return agentType
    }
  }

  const openAgentDetails = (agentId: string) => {
    setSelectedAgent(agentId)
    setDialogOpen(true)
  }

  if (loading) {
    return (
      <Box p={3} sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
        <Typography variant="h4" component="h1" fontWeight="bold" mb={3}>
          🤖 AI Agents Dashboard
        </Typography>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <Box textAlign="center">
            <CircularProgress />
            <Typography variant="body2" color="textSecondary" mt={2}>
              Loading agent data...
            </Typography>
          </Box>
        </Box>
      </Box>
    )
  }

  if (error) {
    return (
      <Box p={3} sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
        <Typography variant="h4" component="h1" fontWeight="bold" mb={3}>
          🤖 AI Agents Dashboard
        </Typography>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={fetchAgentData}>
            Retry
          </Button>
        }>
          {error}
        </Alert>
      </Box>
    )
  }

  return (
    <Box p={3} sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          🤖 AI Agents Dashboard
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchAgentData}
        >
          Refresh
        </Button>
      </Box>

      {/* Debug Information */}
      <Alert severity="info" sx={{ mb: 2 }}>
        Debug: Agent Status: {agentStatus ? 'Loaded' : 'Not loaded'} | 
        Events: {events.length} | 
        Metrics: {metrics ? 'Loaded' : 'Not loaded'} |
        Backend: http://localhost:8000/api/v1/agents/ |
        Status: {debugInfo}
      </Alert>

      {/* API Test Button */}
      <Box mb={2}>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={async () => {
            try {
              const response = await fetch('http://localhost:8000/api/v1/agents/')
              const data = await response.json()
              console.log('Direct API test:', data)
              alert(`API Test: ${response.ok ? 'Success' : 'Failed'} - Status: ${response.status}`)
            } catch (err) {
              console.error('Direct API test failed:', err)
              alert(`API Test Failed: ${err}`)
            }
          }}
        >
          Test API Connection
        </Button>
      </Box>

      {/* System Overview */}
      {agentStatus && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      System Status
                    </Typography>
                    <Typography variant="h6">
                      <Chip 
                        label={agentStatus.system_status.toUpperCase()} 
                        color={agentStatus.system_status === 'operational' ? 'success' : 'error'}
                      />
                    </Typography>
                  </Box>
                  {agentStatus.system_status === 'operational' ? 
                    <CheckCircle color="success" /> : 
                    <Error color="error" />
                  }
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Agents
                    </Typography>
                    <Typography variant="h4">
                      {agentStatus.total_agents}
                    </Typography>
                  </Box>
                  <Memory color="primary" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Active Agents
                    </Typography>
                    <Typography variant="h4" color="success.main">
                      {agentStatus.active_agents}
                    </Typography>
                  </Box>
                  <CheckCircle color="success" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      System Health
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={(agentStatus.active_agents / agentStatus.total_agents) * 100}
                      color="success"
                    />
                    <Typography variant="caption" color="textSecondary">
                      {Math.round((agentStatus.active_agents / agentStatus.total_agents) * 100)}% Operational
                    </Typography>
                  </Box>
                  <Speed color="info" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Agent Cards */}
      {agentStatus && (
        <>
          <Typography variant="h5" component="h2" gutterBottom mb={2}>
            Active Agents
          </Typography>
          <Grid container spacing={3} mb={4}>
            {Object.entries(agentStatus.agents).map(([agentId, agent]) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={agentId}>
                <Card elevation={2} sx={{ height: '100%' }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                      <Box display="flex" alignItems="center">
                        <Typography variant="h4" sx={{ mr: 1 }}>
                          {getAgentIcon(agent.agent_type)}
                        </Typography>
                        <Box>
                          <Typography variant="h6" fontWeight="bold">
                            {getAgentDisplayName(agent.agent_type)}
                          </Typography>
                          <Chip 
                            label={agent.status} 
                            size="small"
                            color={getStatusColor(agent.status)}
                          />
                        </Box>
                      </Box>
                      <Tooltip title="Agent Details">
                        <IconButton onClick={() => openAgentDetails(agentId)}>
                          <Info />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      {agent.message}
                    </Typography>
                    
                    <Typography variant="caption" color="textSecondary">
                      Last Activity: {new Date(agent.last_activity).toLocaleTimeString()}
                    </Typography>
                    
                    <Box mt={2} display="flex" gap={1}>
                      <Button size="small" startIcon={<PlayArrow />} color="success">
                        Start
                      </Button>
                      <Button size="small" startIcon={<Pause />} color="warning">
                        Pause
                      </Button>
                      <Button size="small" startIcon={<Settings />} color="primary">
                        Config
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      {/* Performance Metrics */}
      {metrics && (
        <>
          <Typography variant="h5" component="h2" gutterBottom mb={2}>
            Performance Metrics
          </Typography>
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    System Performance
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Uptime
                      </Typography>
                      <Typography variant="h6">
                        {metrics.system_metrics.uptime_hours.toFixed(1)}h
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Messages Processed
                      </Typography>
                      <Typography variant="h6">
                        {metrics.system_metrics.messages_processed.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Avg Response Time
                      </Typography>
                      <Typography variant="h6">
                        {metrics.system_metrics.average_response_time.toFixed(2)}ms
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Error Rate
                      </Typography>
                      <Typography variant="h6" color={metrics.system_metrics.error_rate > 0.05 ? 'error' : 'success'}>
                        {(metrics.system_metrics.error_rate * 100).toFixed(2)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Agent Events
                  </Typography>
                  <List dense>
                    {events.slice(0, 5).map((event, index) => (
                      <ListItem key={index} divider>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Chip 
                                label={event.severity} 
                                size="small" 
                                color={getSeverityColor(event.severity)}
                              />
                              <Typography variant="body2">
                                {event.message}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Typography variant="caption" color="textSecondary">
                              {event.agent_id} • {new Date(event.timestamp).toLocaleTimeString()}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}

      {/* Agent Details Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Agent Details: {selectedAgent && agentStatus ? 
            getAgentDisplayName(agentStatus.agents[selectedAgent].agent_type) : 'Unknown'}
        </DialogTitle>
        <DialogContent>
          {selectedAgent && agentStatus && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">Status</Typography>
                  <Chip 
                    label={agentStatus.agents[selectedAgent].status} 
                    color={getStatusColor(agentStatus.agents[selectedAgent].status)}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">Agent Type</Typography>
                  <Typography>{agentStatus.agents[selectedAgent].agent_type}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Current Activity</Typography>
                  <Typography>{agentStatus.agents[selectedAgent].message}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">Last Activity</Typography>
                  <Typography>{new Date(agentStatus.agents[selectedAgent].last_activity).toLocaleString()}</Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default AgentsPage
