# Hospital Operations Platform - Setup Instructions

## Current Situation
You have Python 3.13.3 and Python 3.10.7 installed. The platform works best with Python 3.10 due to better package compatibility.

## Quick Setup Steps

### Option 1: Use Core Dependencies (Recommended for Testing)
```powershell
# Run the quick setup script
.\quick-setup.bat

# Then validate
venv\Scripts\activate
python validate-system.py
```

### Option 2: Manual Setup with Python 3.10
```powershell
# Create venv with Python 3.10
py -3.10 -m venv venv
# OR if you have python3.10 in PATH:
python3.10 -m venv venv

# Activate environment
venv\Scripts\activate

# Install core dependencies
pip install -r requirements-core.txt

# Validate system
python validate-system.py
```

### Option 3: Full Setup (All Features)
```powershell
# After core setup works, install full requirements
venv\Scripts\activate
pip install -r requirements.txt
```

## Files Created/Updated

1. **requirements-core.txt** - Minimal dependencies for core functionality
2. **quick-setup.bat** - Automated setup script using Python 3.10
3. **setup-python310.bat** - Comprehensive setup script
4. **Updated requirements.txt** - Version ranges for better compatibility
5. **Updated validate-system.py** - Better handling of optional dependencies
6. **Updated config.py** - Fallback for missing pydantic-settings

## What's Fixed

1. ✅ **Python Version Compatibility** - Now supports Python 3.10-3.12
2. ✅ **TensorFlow Issue** - Updated to compatible versions
3. ✅ **Dependency Conflicts** - Using version ranges instead of pinned versions
4. ✅ **Core vs Optional** - Separated essential from optional dependencies
5. ✅ **Setup Scripts** - Automated setup for Python 3.10

## Next Steps

1. Run `quick-setup.bat` 
2. Run `python validate-system.py`
3. If all core checks pass, run `start-platform.bat`

## Troubleshooting

- If Python 3.10 is not found, install it from python.org
- If packages fail to install, try upgrading pip: `python -m pip install --upgrade pip`
- For full AI features, install the complete requirements.txt after core setup works
