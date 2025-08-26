# Installation and Setup Script for Browser Controller

## Quick Start

### 1. Install Python Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### 2. Install Browser Drivers
The Browser Controller uses webdriver-manager to automatically download and manage browser drivers. No manual installation required!

For manual installation:
```bash
# Chrome
# Download from: https://chromedriver.chromium.org/

# Firefox  
# Download from: https://github.com/mozilla/geckodriver/releases

# Edge
# Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
```

### 3. Configuration
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your preferred settings:
```bash
BROWSER_TYPE=chrome
BROWSER_HEADLESS=true
BROWSER_WIDTH=1920
BROWSER_HEIGHT=1080
```

### 4. Test Installation
```python
from browser_controller import create_browser_controller

# Create and test browser controller
controller = create_browser_controller("chrome", headless=True)
print(f"Browser Controller created: {controller}")
```

### 5. Run Examples
```bash
# Run basic usage example
python examples/basic_usage.py

# Run specific example
python -c "from examples.basic_usage import basic_usage_example; import asyncio; asyncio.run(basic_usage_example())"
```

## Installation Options

### Option 1: Pip Install (Recommended)
```bash
pip install browser_controller
```

### Option 2: Development Install
```bash
git clone https://github.com/Large-Action-Model/browser_controller.git
cd browser_controller
pip install -e .[dev]
```

### Option 3: Docker Install
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

CMD ["python", "examples/basic_usage.py"]
```

## Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver Version Mismatch**
   ```bash
   # Update webdriver-manager
   pip install --upgrade webdriver-manager
   ```

2. **Permission Denied on Linux/Mac**
   ```bash
   # Make driver executable
   chmod +x /path/to/chromedriver
   ```

3. **Headless Mode Not Working**
   ```python
   # Try different headless options
   config = BrowserConfig(
       browser_type="chrome",
       headless=True,
       browser_args=["--no-sandbox", "--disable-dev-shm-usage"]
   )
   ```

4. **SSL Certificate Errors**
   ```python
   config = BrowserConfig(
       ignore_certificate_errors=True
   )
   ```

### Environment-Specific Setup

#### Windows
```bash
# PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Linux (Ubuntu/Debian)
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install Chrome dependencies
sudo apt install -y wget gnupg
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
sudo apt update
sudo apt install google-chrome-stable

# Create virtual environment
python3 -m venv venv  
source venv/bin/activate
pip install -r requirements.txt
```

## Development Setup

### Code Quality Tools
```bash
# Install development dependencies
pip install -e .[dev]

# Format code
black src/ examples/ tests/
isort src/ examples/ tests/

# Lint code
flake8 src/ examples/ tests/
mypy src/

# Run tests
pytest tests/
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Verification

Run this verification script to ensure everything is working:

```python
import asyncio
from browser_controller import create_browser_controller

async def verify_installation():
    """Verify Browser Controller installation."""
    try:
        # Test browser creation
        controller = create_browser_controller("chrome", headless=True)
        print("✓ Browser Controller created successfully")
        
        # Test browser launch
        async with controller as browser:
            print("✓ Browser launched successfully")
            
            # Test navigation
            result = await browser.navigate_to("https://httpbin.org/")
            print(f"✓ Navigation successful: {result.success}")
            
            # Test page info
            page_info = await browser.get_page_info()
            print(f"✓ Page info retrieved: {page_info.title}")
            
        print("✓ All tests passed! Browser Controller is ready to use.")
        
    except Exception as e:
        print(f"✗ Installation verification failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(verify_installation())
```

Save this as `verify_installation.py` and run:
```bash
python verify_installation.py
```
