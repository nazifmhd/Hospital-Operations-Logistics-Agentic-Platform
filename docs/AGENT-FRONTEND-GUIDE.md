# How to View AI Agents in the Frontend

## 🤖 Multi-Agent System Overview

The Hospital Operations & Logistics Agentic Platform features a sophisticated multi-agent system with 4 specialized AI agents:

### 🏥 Available Agents

1. **🛏️ Bed Management Agent**
   - Optimizes bed allocation and patient flow
   - Predicts bed availability
   - Coordinates with other agents for admissions

2. **🔧 Equipment Tracker Agent**
   - Tracks equipment location and utilization
   - Manages maintenance schedules
   - Optimizes equipment distribution

3. **👥 Staff Allocation Agent**
   - Optimizes staffing levels and schedules
   - Matches staff skills to requirements
   - Manages workload balancing

4. **📦 Supply Inventory Agent**
   - Manages inventory levels
   - Automates reordering processes
   - Monitors supply chain optimization

## 📱 How to View Agents in Frontend

### Method 1: Dedicated Agents Page
1. **Start the Application**:
   ```bash
   # Terminal 1: Start Backend
   cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2: Start Frontend
   cd frontend && npm start
   ```

2. **Navigate to Agents Dashboard**:
   - Open browser: `http://localhost:3000`
   - Click on **"Agents"** in the left sidebar (🤖 icon)
   - URL: `http://localhost:3000/agents`

3. **What You'll See**:
   - **System Overview**: Status cards showing system health
   - **Agent Cards**: Individual agent status with controls
   - **Performance Metrics**: System-wide performance data
   - **Recent Events**: Live agent activity feed
   - **Agent Details**: Click info button for detailed view

### Method 2: Analytics Page
1. **Navigate to Analytics**:
   - Click on **"Analytics"** in the left sidebar (📊 icon)
   - URL: `http://localhost:3000/analytics`

2. **Scroll to Agent Section**:
   - Look for "Agent System Status" section
   - Shows compact agent status cards
   - Displays system operational status

## 🎛️ Agent Dashboard Features

### 📊 System Status Cards
- **System Status**: Overall operational status
- **Total Agents**: Number of configured agents (4)
- **Active Agents**: Currently running agents
- **System Health**: Health percentage with progress bar

### 🤖 Individual Agent Cards
Each agent card shows:
- **Agent Icon**: Visual identifier (🛏️🔧👥📦)
- **Agent Name**: Human-readable name
- **Status Chip**: Current status (Running/Error/Paused)
- **Activity Message**: Current task description
- **Last Activity**: Timestamp of last activity
- **Control Buttons**: Start/Pause/Config actions

### 📈 Performance Metrics
- **System Uptime**: Hours of continuous operation
- **Messages Processed**: Inter-agent communications
- **Average Response Time**: System responsiveness
- **Error Rate**: System reliability metric

### 📋 Recent Events
Live feed showing:
- **Agent Activity**: Real-time agent actions
- **Event Types**: bed_allocation, maintenance_alert, etc.
- **Severity Levels**: Info/Warning/Error indicators
- **Timestamps**: When events occurred

### 🔍 Agent Details Dialog
Click the info (ℹ️) button on any agent card to see:
- **Detailed Status**: Current operational state
- **Agent Type**: Technical classification
- **Current Activity**: Detailed description
- **Last Activity**: Full timestamp

## 🔧 API Endpoints

The frontend fetches data from these backend endpoints:

### Agent Status
```http
GET /api/v1/agents/
```
Returns system and individual agent status.

### Agent Events
```http
GET /api/v1/agents/events
```
Returns recent agent activity events.

### Performance Metrics
```http
GET /api/v1/agents/metrics/performance
```
Returns system-wide performance data.

## 🔄 Real-Time Updates

The Agents dashboard automatically refreshes every 10 seconds to show:
- Live agent status changes
- New events and activities
- Updated performance metrics
- System health changes

## 🎯 Key Features

### 🟢 Live Status Monitoring
- Real-time agent health status
- System operational indicators
- Performance trend monitoring

### 🎮 Agent Control Interface
- Start/stop individual agents
- Configure agent parameters
- Monitor agent activities

### 📊 Performance Analytics
- System uptime tracking
- Message processing metrics
- Error rate monitoring
- Response time analysis

### 🚨 Event Tracking
- Real-time activity feed
- Severity-based filtering
- Agent-specific events
- Historical event log

## 🛠️ Testing Agent Functionality

You can test the agent system using the provided test script:

```bash
python test-agents.py
```

This will verify:
- All API endpoints are responding
- Agents are operational
- System status is healthy
- Performance metrics are available

## 📱 Navigation

**Left Sidebar Menu Items:**
- 🏠 **Dashboard**: Main overview
- 🛏️ **Beds**: Bed management
- 🔧 **Equipment**: Equipment tracking  
- 👥 **Staff**: Staff allocation
- 📦 **Supplies**: Supply inventory
- 📊 **Analytics**: Comprehensive analytics (includes agents)
- 🤖 **Agents**: Dedicated agent dashboard

## 🎉 Summary

The multi-agent system is fully integrated into the frontend with two main viewing options:

1. **Primary**: Dedicated `/agents` page with comprehensive dashboard
2. **Secondary**: Agent status section in `/analytics` page

Both provide real-time monitoring, performance metrics, and agent control capabilities, giving you complete visibility into the AI agent ecosystem powering your hospital operations platform.
