#!/bin/bash
# MongoDB Helper Script for Kuberan

case "$1" in
  start)
    echo "Starting MongoDB and backend services..."
    docker-compose up -d
    echo "✓ Services started!"
    echo "MongoDB: mongodb://localhost:27017"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    ;;
  
  stop)
    echo "Stopping services..."
    docker-compose down
    echo "✓ Services stopped!"
    ;;
  
  restart)
    echo "Restarting services..."
    docker-compose restart
    echo "✓ Services restarted!"
    ;;
  
  logs)
    if [ -z "$2" ]; then
      docker-compose logs -f
    else
      docker-compose logs -f "$2"
    fi
    ;;
  
  shell)
    echo "Connecting to MongoDB shell..."
    docker exec -it kuberan-mongodb mongosh kuberan
    ;;
  
  status)
    echo "Service status:"
    docker-compose ps
    ;;
  
  clean)
    echo "⚠️  This will remove all MongoDB data. Are you sure? (yes/no)"
    read -r response
    if [ "$response" = "yes" ]; then
      docker-compose down -v
      echo "✓ All data cleared!"
    else
      echo "Cancelled."
    fi
    ;;
  
  backup)
    echo "Creating MongoDB backup..."
    docker exec kuberan-mongodb mongodump --db=kuberan --out=/data/backup
    docker cp kuberan-mongodb:/data/backup ./mongodb_backup_$(date +%Y%m%d_%H%M%S)
    echo "✓ Backup created!"
    ;;
  
  *)
    echo "Kuberan MongoDB Helper"
    echo ""
    echo "Usage: ./scripts/mongodb.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start MongoDB and backend services"
    echo "  stop     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  logs     - View logs (optionally specify service: mongodb or backend)"
    echo "  shell    - Connect to MongoDB shell"
    echo "  status   - Show service status"
    echo "  clean    - Remove all data (WARNING: destructive)"
    echo "  backup   - Create a backup of MongoDB data"
    echo ""
    echo "Examples:"
    echo "  ./scripts/mongodb.sh start"
    echo "  ./scripts/mongodb.sh logs backend"
    echo "  ./scripts/mongodb.sh shell"
    ;;
esac
