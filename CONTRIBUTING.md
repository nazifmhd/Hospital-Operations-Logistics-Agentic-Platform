# Contributing to Hospital Operations & Logistics Agentic Platform

First off, thank you for considering contributing to the Hospital Operations & Logistics Agentic Platform! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Node.js 18 or higher
- Git

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/Hospital-Operations-Logistics-Agentic-Platform.git
   cd Hospital-Operations-Logistics-Agentic-Platform
   ```

2. **Set up the backend**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Create environment file**
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/macOS
   ```

5. **Test the setup**
   ```bash
   # Terminal 1: Start backend
   python start-api-only.py
   
   # Terminal 2: Start frontend
   cd frontend && npm run dev
   ```

## 🛠️ How to Contribute

### Types of Contributions

We welcome various types of contributions:
- 🐛 **Bug fixes**
- ✨ **New features**
- 📝 **Documentation improvements**
- 🧪 **Tests**
- 🎨 **UI/UX improvements**
- 🔧 **Performance optimizations**

### Before You Start

1. **Check existing issues** - Look for existing issues or create a new one
2. **Discuss major changes** - For large features, discuss with maintainers first
3. **Follow coding standards** - See our coding standards below

## 💻 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

### 2. Make Your Changes

#### Backend Changes (Python)
- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Update API documentation if needed
- Add tests for new functionality

#### Frontend Changes (React/TypeScript)
- Follow TypeScript best practices
- Use Material-UI components consistently
- Ensure responsive design
- Add error handling

### 3. Test Your Changes

```bash
# Backend testing
python -m pytest tests/ -v

# Frontend testing
cd frontend
npm test

# Manual testing
# Start both backend and frontend, test functionality
```

### 4. Update Documentation

- Update README.md if needed
- Add API documentation for new endpoints
- Update CHANGELOG.md

## 📤 Pull Request Process

### Before Submitting

- [ ] Code follows our coding standards
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No merge conflicts with main branch
- [ ] Descriptive commit messages

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 📏 Coding Standards

### Python (Backend)

```python
# Use type hints
def get_bed_status(bed_id: str) -> BedStatus:
    """Get the current status of a bed."""
    pass

# Follow PEP 8
class BedManagementAgent:
    """Agent for managing hospital beds."""
    
    def __init__(self, config: AgentConfig) -> None:
        self.config = config

# Use docstrings
def calculate_occupancy_rate(department: str) -> float:
    """
    Calculate the occupancy rate for a department.
    
    Args:
        department: The department name
        
    Returns:
        Occupancy rate as a percentage (0-100)
    """
    pass
```

### TypeScript (Frontend)

```typescript
// Use proper interfaces
interface BedData {
  id: string;
  roomNumber: string;
  department: string;
  status: BedStatus;
}

// Use proper error handling
const fetchBeds = async (): Promise<BedData[]> => {
  try {
    const response = await api.get('/beds');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch beds:', error);
    throw error;
  }
};

// Use meaningful component names
const BedManagementTable: React.FC<BedManagementProps> = ({ onBedSelect }) => {
  // Component implementation
};
```

## 🧪 Testing Guidelines

### Backend Tests

```python
# tests/test_bed_management.py
import pytest
from src.models.bed_models import Bed
from src.api.endpoints.beds import get_beds

def test_get_beds():
    """Test getting all beds."""
    beds = get_beds()
    assert isinstance(beds, list)
    assert len(beds) >= 0

def test_bed_creation():
    """Test creating a new bed."""
    bed_data = {
        "room_number": "101",
        "department": "ICU",
        "bed_type": "ICU"
    }
    bed = Bed(**bed_data)
    assert bed.room_number == "101"
```

### Frontend Tests

```typescript
// frontend/src/components/__tests__/BedTable.test.tsx
import { render, screen } from '@testing-library/react';
import BedTable from '../BedTable';

describe('BedTable', () => {
  test('renders bed table', () => {
    const mockBeds = [
      { id: '1', roomNumber: '101', department: 'ICU', status: 'available' }
    ];
    
    render(<BedTable beds={mockBeds} />);
    expect(screen.getByText('101')).toBeInTheDocument();
  });
});
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Environment information**
   - OS and version
   - Python version
   - Node.js version

2. **Steps to reproduce**
   - Clear, step-by-step instructions

3. **Expected vs actual behavior**
   - What you expected to happen
   - What actually happened

4. **Error messages**
   - Full error messages and stack traces

5. **Screenshots** (if applicable)
   - Visual bugs should include screenshots

## 💡 Suggesting Features

For feature requests:

1. **Use case** - Describe the problem you're trying to solve
2. **Proposed solution** - Your suggested approach
3. **Alternatives** - Other solutions you've considered
4. **Additional context** - Any other relevant information

## 📞 Getting Help

- 📚 **Documentation**: Check the [docs](docs/) directory
- 🐛 **Issues**: Search existing [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **Discussions**: Use [GitHub Discussions](https://github.com/your-repo/discussions)
- 📧 **Email**: Contact maintainers at dev@hospital-platform.com

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Annual contributor appreciation

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the Hospital Operations & Logistics Agentic Platform! 🏥✨
