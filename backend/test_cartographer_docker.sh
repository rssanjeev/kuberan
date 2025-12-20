#!/bin/bash
# Test Cartographer in Docker Environment
# Last Updated: 2025-12-20

set -e

echo "🐳 Testing Cartographer in Docker..."
echo ""

echo "Step 1: Rebuilding Docker image with Playwright dependencies..."
docker-compose build backend

echo ""
echo "Step 2: Starting services..."
docker-compose up -d

echo ""
echo "Step 3: Waiting for backend to be ready..."
sleep 5

echo ""
echo "Step 4: Checking if Playwright is installed..."
docker exec kuberan-backend-1 playwright --version || {
    echo "❌ Playwright not installed in container!"
    exit 1
}

echo ""
echo "Step 5: Running Cartographer test inside container..."
docker exec kuberan-backend-1 python3 -m app.services.cartographer.test_finviz

echo ""
echo "Step 6: Checking generated dictionary..."
docker exec kuberan-backend-1 ls -lh /app/data/site_dictionaries/finviz_dictionary.json || {
    echo "⚠️  Dictionary file not found in expected location"
    echo "Checking alternative locations..."
    docker exec kuberan-backend-1 find /app -name "finviz_dictionary.json" 2>/dev/null
}

echo ""
echo "✅ Cartographer test complete!"
echo ""
echo "To view logs:"
echo "  docker logs kuberan-backend-1 --tail 50"
echo ""
echo "To inspect the dictionary:"
echo "  docker exec kuberan-backend-1 cat /app/data/site_dictionaries/finviz_dictionary.json | jq ."
