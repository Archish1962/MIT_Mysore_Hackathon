#!/bin/bash

# ISTVON Enhancement App Launch Script
# One-command deployment and execution

set -e  # Exit on any error

echo "🚀 ISTVON Enhancement App - Launch Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is not installed. Please install pip."
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created"
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_status "Activating virtual environment and installing dependencies..."
    
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
}

# Check for API key
check_api_key() {
    print_status "Checking for Gemini API key..."
    
    if [ -z "$GEMINI_API_KEY" ]; then
        print_warning "GEMINI_API_KEY environment variable not set."
        print_warning "The app will run in fallback mode (rule-based processing only)."
        print_warning "To enable LLM features, set your Gemini API key:"
        print_warning "export GEMINI_API_KEY='your-api-key-here'"
    else
        print_success "Gemini API key found"
    fi
}

# Run tests (optional)
run_tests() {
    if [ "$1" = "--test" ]; then
        print_status "Running tests..."
        source venv/bin/activate
        python -m pytest tests/ -v
        print_success "Tests completed"
    fi
}

# Start the application
start_app() {
    print_status "Starting ISTVON Enhancement App..."
    
    source venv/bin/activate
    
    # Set environment variables
    export STREAMLIT_SERVER_HEADLESS=true
    export STREAMLIT_SERVER_PORT=8501
    
    print_success "Application starting on http://localhost:8501"
    print_status "Press Ctrl+C to stop the application"
    
    # Start Streamlit
    streamlit run app.py --server.port 8501 --server.headless true
}

# Main execution
main() {
    echo ""
    print_status "Starting ISTVON Enhancement App deployment..."
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    # Setup environment
    setup_venv
    install_dependencies
    
    # Check configuration
    check_api_key
    
    # Run tests if requested
    if [ "$1" = "--test" ]; then
        run_tests "$1"
    fi
    
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    
    # Start the application
    start_app
}

# Handle command line arguments
case "$1" in
    --help|-h)
        echo "ISTVON Enhancement App Launch Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --test     Run tests before starting the app"
        echo "  --help     Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  GEMINI_API_KEY    Set your Gemini API key for LLM features"
        echo ""
        echo "Examples:"
        echo "  $0                # Start the app normally"
        echo "  $0 --test         # Run tests then start the app"
        echo "  GEMINI_API_KEY='your-key' $0  # Start with API key"
        exit 0
        ;;
    --test)
        main "$1"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        print_status "Use --help for usage information"
        exit 1
        ;;
esac
