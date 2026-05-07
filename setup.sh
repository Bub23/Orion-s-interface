#!/bin/bash

echo "=== Orion Local AI System Setup ==="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Install Docker Desktop first."
    exit 1
fi

# Check if .env exists
if [ -f .env ]; then
    echo ".env file already exists."
    read -p "Overwrite it? (y/n): " response
    if [ "$response" != "y" ]; then
        echo "Skipping .env setup."
    else
        rm .env
    fi
fi

# Create .env if missing
if [ ! -f .env ]; then
    echo ""
    echo "Enter your NVIDIA API key:"
    read -r api_key

    if [ -z "$api_key" ]; then
        echo "ERROR: API key cannot be empty"
        exit 1
    fi

    cat > .env << EOF
NVIDIA_API_KEY=$api_key
NVIDIA_MODEL=deepseek-ai/deepseek-v4-pro
EOF

    echo "✓ .env created"
fi

echo ""
echo "=== NEXT STEPS ==="
echo ""
echo "1. Build container:"
echo "   docker-compose build"
echo ""
echo "2. Start system:"
echo "   docker-compose up -d"
echo ""
echo "3. Enter container:"
echo "   docker exec -it ai-system bash"
echo ""
echo "4. Run AI:"
echo "   python main.py"
echo ""