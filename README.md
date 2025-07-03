# 🏥 Hospital Operations & Logistics Agentic Platform

A professional-grade, production-ready platform for autonomous hospital operations management using an agent-based architecture. The system intelligently manages bed allocation, equipment tracking, staff scheduling, and supply inventory through specialized AI agents.

## 🏥 Overview

This platform revolutionizes hospital operations through intelligent automation:

- **🛏️ Autonomous Bed Management** - Real-time bed allocation and patient flow optimization
- **🔧 Smart Equipment Tracking** - RTLS-based equipment monitoring and predictive maintenance
- **👥 Intelligent Staff Allocation** - AI-powered scheduling and workload optimization
- **📦 Automated Supply Management** - Predictive inventory management and automated procurement

## 🏗️ Architecture

### Agent-Based System
- **Agent Orchestrator** - Central coordination and communication hub
- **Bed Management Agent** - Bed allocation, patient flow, discharge planning
- **Equipment Tracker Agent** - Asset tracking, utilization analytics, maintenance scheduling
- **Staff Allocation Agent** - Workforce optimization, skill-based assignments, workload balancing
- **Supply Inventory Agent** - Inventory tracking, demand forecasting, automated ordering

### Technology Stack
- **Backend**: Python 3.8+, FastAPI, SQLAlchemy, Pydantic, SQLite
- **Frontend**: React 18, TypeScript, Material-UI, Vite, Axios
- **Development**: Node.js, npm, Git
- **API**: RESTful APIs with OpenAPI documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 18+
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd Hospital-Operations-Logistics-Agentic-Platform
   ```

2. **Setup Backend**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Start the Application**
   ```bash
   # Start backend (from root directory)
   python start-api-only.py
   
   # Start frontend (in new terminal)
   cd frontend
   npm run dev
   ```

5. **Access the platform**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## ✅ Current Features (Working)

### 🛏️ **Bed Management**
- Real-time bed status tracking (available, occupied, maintenance)
- Bed allocation by department (ICU, Emergency, General, etc.)
- Complete CRUD operations (Create, Read, Update, Delete)
- Bed analytics and occupancy reports

### 👨‍⚕️ **Staff Management** 
- Staff directory with roles and departments
- Duty status tracking (on_duty, off_duty, break)
- Contact information management
- Staff scheduling and allocation

### 🏥 **Equipment Management**
- Medical equipment inventory tracking
- Equipment status monitoring (available, in_use, maintenance)
- Location and department assignments
- Usage hours and maintenance scheduling

### 📦 **Supply Management**
- Medical supplies inventory control
- Stock level monitoring with alerts
- Minimum threshold and maximum capacity tracking
- Supply categories (PPE, Medication, Surgical, etc.)
- Expiry date management

### 📊 **Analytics Dashboard**
- Real-time operational overview
- Key performance indicators (KPIs)
- Department-wise statistics
- Resource utilization metrics

### 🔧 **API Features**
- RESTful API with OpenAPI documentation
- Health check endpoints
- CRUD operations for all entities
- Real-time data synchronization

## 📊 Features

### Real-Time Dashboard
- Live operational metrics and KPIs
- Agent status monitoring
- Alert management
- Performance analytics

### Bed Management
- Real-time bed availability tracking
- Automated patient placement
- Discharge planning and bed turnover optimization
- Capacity forecasting and planning

### Equipment Tracking
- RTLS-based asset location tracking
- Utilization analytics and optimization
- Predictive maintenance scheduling
- Equipment allocation and availability

### Staff Management
- Intelligent shift scheduling
- Skill-based task assignment
- Workload balancing and optimization
- Compliance and certification tracking

### Supply Chain
- Automated inventory monitoring
- Predictive demand forecasting
- Automated procurement workflows
- Expiry and compliance tracking

## 🔧 Configuration

### Environment Variables
Configure the platform using environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_ops
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key

# Agent Configuration
AGENT_TICK_INTERVAL=30
MAX_CONCURRENT_AGENTS=10

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

### Agent Configuration
Each agent can be configured independently:

```python
# Bed Management Agent
BED_PREDICTION_WINDOW_HOURS = 24
BED_OPTIMIZATION_INTERVAL = 300

# Equipment Agent  
EQUIPMENT_TRACKING_INTERVAL = 60
MAINTENANCE_ALERT_DAYS = 7

# Staff Agent
STAFF_REBALANCING_THRESHOLD = 0.8
OVERTIME_WARNING_HOURS = 10

# Supply Agent
AUTO_PROCUREMENT_ENABLED = true
LEAD_TIME_DAYS = 3
SAFETY_STOCK_MULTIPLIER = 1.5
```

## 📡 API Documentation

The platform provides comprehensive REST APIs:

### Core Endpoints
- `GET /health` - System health check
- `GET /api/agents/status` - Agent status and metrics

### Bed Management
- `GET /api/beds/status` - Bed availability summary
- `GET /api/beds/list` - List all beds with filters
- `POST /api/beds/allocate` - Request bed allocation
- `GET /api/beds/forecast` - Capacity forecasting

### Equipment Tracking
- `GET /api/equipment/status` - Equipment status summary
- `GET /api/equipment/list` - Equipment inventory
- `GET /api/equipment/track/{asset_id}` - Track specific equipment
- `POST /api/equipment/request` - Request equipment allocation

### Staff Management
- `GET /api/staff/status` - Staffing status summary
- `GET /api/staff/list` - Staff directory
- `POST /api/staff/allocate` - Staff allocation request
- `GET /api/staff/schedules` - Staff schedules

### Supply Management
- `GET /api/supplies/status` - Inventory status
- `GET /api/supplies/list` - Supply inventory
- `GET /api/supplies/low-stock` - Low stock alerts
- `POST /api/supplies/order` - Create procurement order

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key authentication for system integrations

### Data Protection
- Encryption at rest and in transit
- HIPAA compliance ready
- Audit logging for all operations
- Data anonymization capabilities

### Network Security
- TLS/SSL encryption
- Network isolation with Docker
- Configurable firewall rules
- VPN support for remote access

## 📈 Monitoring & Analytics

### Metrics & Dashboards
- Real-time operational dashboards
- Performance metrics and KPIs
- Agent health and status monitoring
- Custom alerting rules

### Prometheus Metrics
- System performance metrics
- Agent-specific metrics
- Business intelligence metrics
- Custom application metrics

### Grafana Dashboards
- Executive summary dashboard
- Operational metrics dashboard
- Agent performance dashboard
- System health dashboard

## 🧪 Testing

### Running Tests
```bash
# Backend tests
pytest tests/ -v --cov=src

# Frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/ -v

# End-to-end tests
pytest tests/e2e/ -v
```

### Test Coverage
- Unit tests for all agents and core modules
- Integration tests for API endpoints
- End-to-end tests for critical workflows
- Performance and load testing

## 🚀 Deployment

### Production Deployment
- Docker containerization for all services
- Multi-environment support (dev/staging/prod)
- Horizontal scaling capabilities
- Load balancing and high availability
- Automated backup and recovery

### Infrastructure Requirements
- **Minimum**: 4 CPU cores, 8GB RAM, 100GB storage
- **Recommended**: 8 CPU cores, 16GB RAM, 500GB storage
- **High Availability**: Load balancer, multiple instances, shared storage

### Cloud Deployment
- AWS, Azure, Google Cloud compatible
- Kubernetes deployment manifests
- Terraform infrastructure as code
- CI/CD pipeline integration

## 🔄 Integration

### Healthcare Systems
- HL7 FHIR standard support
- EMR system integration
- Laboratory information systems
- Pharmacy management systems

### IoT & Sensors
- RTLS (Real-Time Location Systems)
- Environmental sensors
- Equipment telemetry
- Patient monitoring devices

### External Services
- Supply chain management systems
- Vendor APIs for procurement
- Notification services (SMS, email)
- Single sign-on (SSO) providers

## 📚 Documentation

### User Guides
- [User Manual](docs/user-guide.md)
- [Administrator Guide](docs/admin-guide.md)
- [API Reference](docs/api-reference.md)

### Developer Documentation
- [Architecture Overview](docs/architecture.md)
- [Agent Development Guide](docs/agent-development.md)
- [Contributing Guidelines](docs/contributing.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes with tests
4. Submit a pull request

See [Contributing Guidelines](docs/contributing.md) for detailed instructions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs](docs/) directory
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@hospital-ops-platform.com

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core agent framework
- ✅ Basic dashboard and monitoring
- ✅ REST API implementation
- ✅ Docker deployment

### Phase 2 (Next)
- 🔄 Advanced analytics and ML models
- 🔄 Mobile applications
- 🔄 Advanced integration capabilities
- 🔄 Enhanced security features

### Phase 3 (Future)
- 🔜 AI-powered predictive analytics
- 🔜 Natural language interfaces
- 🔜 Advanced IoT integration
- 🔜 Multi-facility support

---

**Built with ❤️ for healthcare innovation**
- **Predictive Analytics**: Machine learning-powered forecasting and decision-making
- **Seamless Integration**: HL7 FHIR-compliant EMR integration
- **HIPAA Compliance**: Full healthcare data protection and privacy
- **Scalable Architecture**: Cloud-native, containerized microservices

## Agent System

### 🏥 Bed Management Agent (BMA)
- Real-time bed status monitoring
- Predictive bed allocation optimization
- Automated patient flow management
- Integration with discharge planning

### 🔧 Equipment Tracker Agent (ETA)
- Real-time location tracking (RTLS)
- Equipment utilization analytics
- Predictive maintenance scheduling
- Optimal distribution management

### 👥 Staff Allocation Agent (SAA)
- Real-time staffing level monitoring
- Predictive staffing need forecasting
- Automated schedule optimization
- Float pool and agency management

### 📦 Supply Inventory Agent (SIA)
- Real-time inventory tracking
- Automated reordering systems
- Expiration date management
- Cost optimization analytics

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Agents**: LangGraph + LangChain
- **AI/ML**: TensorFlow, PyTorch, scikit-learn
- **Database**: PostgreSQL, InfluxDB, Redis
- **Message Queue**: Apache Kafka

### Frontend
- **Web**: React.js + TypeScript
- **Mobile**: React Native
- **UI Framework**: Material-UI
- **Real-time**: WebSocket + SSE

### Infrastructure
- **Containers**: Docker + Kubernetes
- **Cloud**: AWS/Azure/GCP
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions

## 📁 Project Structure

```
Hospital-Operations-Logistics-Agentic-Platform/
├── 📁 docs/                        # Documentation
│   ├── research/                   # Background research
│   ├── requirements/              # Requirements specifications  
│   ├── architecture/              # System architecture
│   └── planning/                  # Project planning
├── 📁 src/                         # Backend source code
│   ├── agents/                    # AI agent implementations
│   ├── core/                      # Core platform services
│   ├── api/                       # REST API endpoints
│   ├── models/                    # Data models and schemas
│   └── utils/                     # Utility functions
├── 📁 frontend/                    # React frontend application
│   ├── src/                       # Frontend source code
│   │   ├── components/            # Reusable UI components
│   │   ├── pages/                 # Main application pages
│   │   ├── services/              # API service layer
│   │   └── types/                 # TypeScript type definitions
│   ├── package.json              # Frontend dependencies
│   └── vite.config.ts            # Vite configuration
├── 📁 config/                      # Configuration files
├── 📁 scripts/                     # Deployment and utility scripts
├── 📄 requirements.txt             # Python dependencies
├── 📄 start-api-only.py           # Backend startup script
├── 📄 .gitignore                  # Git ignore rules
└── 📄 README.md                   # This file
```

## Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 18+
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd Hospital-Operations-Logistics-Agentic-Platform
   ```

2. **Backend Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   venv\Scripts\activate          # Windows
   # source venv/bin/activate     # Linux/macOS
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment template
   copy .env.example .env          # Windows
   # cp .env.example .env          # Linux/macOS
   
   # Edit .env file with your settings
   ```

5. **Start the Application**
   ```bash
   # Terminal 1: Start Backend
   python start-api-only.py
   
   # Terminal 2: Start Frontend  
   cd frontend
   npm run dev
   ```

6. **Access the Application**
   - 🌐 **Frontend**: http://localhost:3000
   - 📡 **API Docs**: http://localhost:8000/docs  
   - ❤️ **Health Check**: http://localhost:8000/health

## Development

### Setting up Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run tests**
   ```bash
   pytest tests/
   ```

3. **Code formatting and linting**
   ```bash
   black src/
   flake8 src/
   mypy src/
   ```

### Agent Development

Each agent follows a standardized structure:

```python
from src.core.base_agent import BaseAgent

class BedManagementAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="bed_management")
        
    async def process_event(self, event):
        # Agent-specific processing logic
        pass
        
    async def make_decision(self, context):
        # Decision-making logic
        pass
```

## API Documentation

The platform exposes RESTful APIs for integration:

- **Agent Management**: `/api/v1/agents/`
- **Bed Operations**: `/api/v1/beds/`
- **Equipment Tracking**: `/api/v1/equipment/`
- **Staff Management**: `/api/v1/staff/`
- **Supply Inventory**: `/api/v1/supplies/`

See the [API Documentation](docs/api/README.md) for detailed endpoint specifications.

## Deployment

### Production Deployment

1. **Build Docker images**
   ```bash
   docker build -t hospital-platform:latest .
   ```

2. **Deploy with Kubernetes**
   ```bash
   kubectl apply -f k8s/
   ```

3. **Configure monitoring**
   ```bash
   helm install monitoring prometheus-community/kube-prometheus-stack
   ```

### Environment Configuration

The platform supports multiple deployment environments:
- **Development**: Local development with hot reload
- **Staging**: Pre-production testing environment
- **Production**: High-availability production deployment

## Security & Compliance

### HIPAA Compliance
- End-to-end encryption for all data
- Role-based access control (RBAC)
- Comprehensive audit logging
- Business Associate Agreement (BAA) support

### Security Features
- Multi-factor authentication (MFA)
- API rate limiting and throttling
- Intrusion detection and prevention
- Regular security assessments

## Monitoring & Observability

### Key Metrics
- **Performance**: Response times, throughput, error rates
- **Business**: Bed utilization, equipment efficiency, cost savings
- **System**: CPU, memory, disk, network utilization
- **Security**: Failed authentication attempts, access violations

### Dashboards
- **Operational Dashboard**: Real-time hospital operations overview
- **Executive Dashboard**: High-level KPIs and trends
- **Technical Dashboard**: System health and performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## Documentation

- [Architecture Overview](docs/architecture/solution_design.md)
- [Agent Definitions](docs/planning/agent_definitions.md)
- [Requirements Specification](docs/requirements/requirements_specification.md)
- [API Reference](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)

## Roadmap

### Phase 1: Foundation (Q1 2025)
- ✅ Project setup and documentation
- 🔄 Core agent framework development
- 🔄 Basic EMR integration
- 🔄 Initial dashboard implementation

### Phase 2: Core Agents (Q2 2025)
- 📋 Bed Management Agent deployment
- 📋 Equipment Tracker Agent implementation
- 📋 Staff Allocation Agent development
- 📋 Basic inter-agent communication

### Phase 3: Advanced Features (Q3 2025)
- 📋 Supply Inventory Agent completion
- 📋 Advanced predictive analytics
- 📋 Mobile application development
- 📋 Performance optimization

### Phase 4: Enterprise Features (Q4 2025)
- 📋 Multi-hospital support
- 📋 Advanced reporting and analytics
- 📋 Third-party integrations
- 📋 Enterprise security features

## Support

For support and questions:
- 📧 Email: support@hospital-platform.com
- 📖 Documentation: [docs.hospital-platform.com](https://docs.hospital-platform.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/Hospital-Operations-Logistics-Agentic-Platform/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/Hospital-Operations-Logistics-Agentic-Platform/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Healthcare informatics research community
- Open source AI/ML frameworks
- Hospital operations management experts
- Healthcare IT standards organizations

---

**Hospital Operations & Logistics Agentic Platform** - Transforming healthcare operations through intelligent automation.

## 🛠️ Troubleshooting

### Common Issues

**Backend won't start:**
- ✅ Check Python version: `python --version` (needs 3.8+)
- ✅ Activate virtual environment: `venv\Scripts\activate`
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Check port 8000 is available

**Frontend won't start:**
- ✅ Check Node.js version: `node --version` (needs 18+)
- ✅ Install dependencies: `cd frontend && npm install`
- ✅ Check port 3000 is available

**API endpoints not working:**
- ✅ Ensure backend is running on http://localhost:8000
- ✅ Check API documentation at http://localhost:8000/docs
- ✅ Verify database file exists: `hospital_platform.db`

**Database issues:**
- ✅ Delete existing database: `del hospital_platform.db` (Windows) / `rm hospital_platform.db` (Linux/macOS)
- ✅ Restart backend to create fresh database

### Getting Help

- 📚 Check the [Documentation](docs/)
- 🐛 Report issues on GitHub
- 💬 Ask questions in Discussions
- 📧 Contact: support@hospital-platform.com