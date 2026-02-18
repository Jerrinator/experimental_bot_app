#!/bin/bash

echo "HERO Assistant Chatbot - Development Setup"
echo "=========================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create one with your configuration."
    echo "See README.md for required environment variables."
fi

# Build the application
echo "Building application..."
npm run build

# Create necessary directories
mkdir -p uploads temp public/downloads logs

echo "Setup complete! You can now start the application with:"
echo "  npm run dev    (development mode)"
echo "  npm start      (production mode)"
echo "  docker-compose up -d (Docker deployment)"
