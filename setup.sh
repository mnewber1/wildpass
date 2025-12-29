#!/bin/bash

# WildPass Setup Script
# This script automates the setup process for the WildPass application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║                                           ║"
echo "║         WildPass Setup Script             ║"
echo "║                                           ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Node.js is installed
echo -e "${YELLOW}Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed. Please install Node.js 14+ and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version) found${NC}"

# Check if Python is installed
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3.8+ and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version) found${NC}"

# Check if pip is installed
echo -e "${YELLOW}Checking pip installation...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip is not installed. Please install pip and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip found${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 1: Backend Environment Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Create .env file from .env.example
if [ -f "backend/.env" ]; then
    echo -e "${YELLOW}backend/.env already exists. Do you want to overwrite it? (y/n)${NC}"
    read -r overwrite
    if [ "$overwrite" != "y" ]; then
        echo -e "${YELLOW}Skipping .env file creation${NC}"
    else
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✓ Created backend/.env from .env.example${NC}"
    fi
else
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ Created backend/.env from .env.example${NC}"
fi

# Ask for Amadeus API credentials
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}Amadeus API Configuration${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Do you want to configure Amadeus API credentials now? (y/n)${NC}"
echo -e "${BLUE}You can also configure them later by editing backend/.env${NC}"
read -r configure_amadeus

if [ "$configure_amadeus" = "y" ]; then
    echo ""
    echo -e "${YELLOW}Please enter your Amadeus API Key:${NC}"
    read -r amadeus_key

    echo -e "${YELLOW}Please enter your Amadeus API Secret:${NC}"
    read -r amadeus_secret

    # Update .env file with credentials
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/AMADEUS_API_KEY=.*/AMADEUS_API_KEY=$amadeus_key/" backend/.env
        sed -i '' "s/AMADEUS_API_SECRET=.*/AMADEUS_API_SECRET=$amadeus_secret/" backend/.env
    else
        # Linux
        sed -i "s/AMADEUS_API_KEY=.*/AMADEUS_API_KEY=$amadeus_key/" backend/.env
        sed -i "s/AMADEUS_API_SECRET=.*/AMADEUS_API_SECRET=$amadeus_secret/" backend/.env
    fi

    echo -e "${GREEN}✓ Amadeus API credentials configured${NC}"
else
    echo -e "${YELLOW}Skipping Amadeus API configuration${NC}"
    echo -e "${YELLOW}To use real flight data, edit backend/.env and add your credentials${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 2: Installing Backend Dependencies${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

cd ..

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 3: Installing Frontend Dependencies${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Install frontend dependencies
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
npm install
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                           ║${NC}"
echo -e "${GREEN}║      Setup completed successfully! 🎉     ║${NC}"
echo -e "${GREEN}║                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}Next Steps:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}1. Start the backend server:${NC}"
echo -e "   ${GREEN}cd backend${NC}"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo -e "   ${GREEN}python app.py${NC}"
echo ""
echo -e "${YELLOW}2. In a new terminal, start the frontend:${NC}"
echo -e "   ${GREEN}npm start${NC}"
echo ""
echo -e "${YELLOW}3. Open your browser to:${NC}"
echo -e "   ${GREEN}http://localhost:3000${NC}"
echo ""

# Ask if user wants to start the servers now
echo -e "${BLUE}Would you like to start both servers now? (y/n)${NC}"
read -r start_servers

if [ "$start_servers" = "y" ]; then
    echo ""
    echo -e "${YELLOW}Starting backend server in the background...${NC}"

    # Start backend in background
    cd backend
    source venv/bin/activate
    python app.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..

    echo -e "${GREEN}✓ Backend server started (PID: $BACKEND_PID)${NC}"
    echo -e "${YELLOW}Backend logs: backend.log${NC}"

    # Wait a moment for backend to start
    sleep 3

    echo ""
    echo -e "${YELLOW}Starting frontend server...${NC}"
    echo -e "${BLUE}Press Ctrl+C to stop both servers${NC}"
    echo ""

    # Trap Ctrl+C to kill both processes
    trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID 2>/dev/null; exit" INT

    # Start frontend (this will run in foreground)
    npm start
else
    echo ""
    echo -e "${GREEN}Setup complete! Follow the steps above to start the servers.${NC}"
    echo ""
fi
