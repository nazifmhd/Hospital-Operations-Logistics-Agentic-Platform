"""
Hospital Operations Platform - System Validation Script
This script validates that all components are properly set up and can run successfully.
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_python_version():
    """Check if Python version is supported"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ is required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported.")
    return True

def check_dependencies():
    """Check if all required dependencies can be imported"""
    print("\nChecking dependencies...")
    
    # Core dependencies (required)
    core_dependencies = [
        "fastapi",
        "uvicorn",
        "sqlalchemy", 
        "pydantic",
        "numpy",
        "pandas"
    ]
    
    # Optional dependencies (nice to have)
    optional_dependencies = [
        "tensorflow",
        "torch",
        "langchain",
        "redis",
        "kafka"
    ]
    
    missing_core = []
    missing_optional = []
    
    for dep in core_dependencies:
        try:
            spec = importlib.util.find_spec(dep)
            if spec is None:
                missing_core.append(dep)
            else:
                print(f"✅ {dep} is available")
        except ImportError:
            missing_core.append(dep)
    
    for dep in optional_dependencies:
        try:
            spec = importlib.util.find_spec(dep)
            if spec is None:
                missing_optional.append(dep)
            else:
                print(f"✅ {dep} is available")
        except ImportError:
            missing_optional.append(dep)
    
    if missing_core:
        print(f"❌ Missing CORE dependencies: {', '.join(missing_core)}")
        print("Run: pip install -r requirements-core.txt")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing OPTIONAL dependencies: {', '.join(missing_optional)}")
        print("Run: pip install -r requirements.txt (for full features)")
    
    return True

def check_project_structure():
    """Check if all required files and directories exist"""
    print("\nChecking project structure...")
    
    required_files = [
        "src/main.py",
        "src/core/config.py",
        "src/core/database.py",
        "src/core/crud.py",
        "src/core/models.py",
        "src/api/routes.py",
        "src/api/endpoints/beds.py",
        "src/api/endpoints/equipment.py",
        "src/api/endpoints/staff.py",
        "src/api/endpoints/supplies.py",
        "src/agents/orchestrator.py",
        "src/models/bed_models.py",
        "src/models/equipment_models.py",
        "src/models/staff_models.py",
        "src/models/supply_models.py",
        "requirements.txt"
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    return True

def check_imports():
    """Check if core modules can be imported without errors"""
    print("\nChecking module imports...")
    
    modules_to_test = [
        ("src.core.config", "settings"),
        ("src.core.database", "get_db"),
        ("src.core.crud", "bed_crud"),
        ("src.api.routes", "api_router"),
        ("src.agents.orchestrator", "AgentOrchestrator"),
    ]
    
    errors = []
    for module_name, attr_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, attr_name):
                print(f"✅ {module_name}.{attr_name}")
            else:
                errors.append(f"Missing attribute {attr_name} in {module_name}")
        except Exception as e:
            errors.append(f"Import error in {module_name}: {str(e)}")
    
    if errors:
        print("❌ Import errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True

def check_configuration():
    """Check if configuration is valid"""
    print("\nChecking configuration...")
    
    try:
        from src.core.config import settings
        
        # Check required settings
        required_settings = ["APP_NAME", "APP_VERSION", "DATABASE_URL", "API_HOST", "API_PORT"]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                print(f"✅ {setting}: {value}")
            else:
                print(f"❌ Missing setting: {setting}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False

def test_database_setup():
    """Test database initialization"""
    print("\nTesting database setup...")
    
    try:
        from src.core.database import engine, SessionLocal
        from src.core.models import Base
        from sqlalchemy import text
        
        # Test database connection
        with SessionLocal() as db:
            # Try a simple query
            result = db.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
        
        print("✅ Database setup is valid")
        return True
    except Exception as e:
        print(f"❌ Database setup error: {str(e)}")
        return False

def generate_report():
    """Generate a comprehensive validation report"""
    print("\n" + "="*60)
    print("HOSPITAL OPERATIONS PLATFORM - VALIDATION REPORT")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Module Imports", check_imports),
        ("Configuration", check_configuration),
        ("Database Setup", test_database_setup),
    ]
    
    results = {}
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        print("-" * 40)
        results[check_name] = check_func()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<30} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! The system is ready to run.")
        print("\nNext steps:")
        print("1. Run: start-platform.bat (to start both backend and frontend)")
        print("2. Or run individually:")
        print("   - Backend: start-backend.bat")
        print("   - Frontend: start-frontend.bat")
        print("3. Access the application:")
        print("   - API: http://localhost:8000")
        print("   - Documentation: http://localhost:8000/docs")
        print("   - Frontend: http://localhost:5173")
    else:
        print(f"\n⚠️  {total-passed} check(s) failed. Please resolve the issues above before running the system.")
    
    return passed == total

if __name__ == "__main__":
    success = generate_report()
    sys.exit(0 if success else 1)
