#!/bin/bash
# Production Deployment Script
# Government AI Personal Assistant - NTR District

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        Production Deployment - RTGS AI Assistant          ║"
echo "║                 NTR District (Vijayawada)                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_DIR="/opt/rtgs-ai-assistant"
BACKUP_DIR="/backup/rtgs-ai"
LOG_FILE="/var/log/rtgs-deployment.log"

# Functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ $1${NC}" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    error "Please do not run as root"
    exit 1
fi

# Step 1: Pre-deployment validation
info "Step 1/10: Running pre-deployment validation..."
python3 pre_deployment_check.py
if [ $? -ne 0 ]; then
    error "Pre-deployment validation failed. Fix issues and try again."
    exit 1
fi
success "Pre-deployment validation passed"

# Step 2: Create backup
info "Step 2/10: Creating backup..."
mkdir -p "$BACKUP_DIR"
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    dashboard/.env.local \
    docker-compose.yml \
    n8n-workflows/ \
    2>/dev/null || warning "Backup completed with warnings"
success "Backup created: $BACKUP_NAME.tar.gz"

# Step 3: Pull latest code (if using git)
if [ -d ".git" ]; then
    info "Step 3/10: Pulling latest code..."
    git pull origin main || warning "Git pull failed or not configured"
    success "Code updated"
else
    warning "Step 3/10: Not a git repository, skipping pull"
fi

# Step 4: Update dependencies
info "Step 4/10: Updating dependencies..."

# Dashboard dependencies
cd dashboard
npm install --production
success "Dashboard dependencies updated"
cd ..

# AI Service dependencies
docker-compose build ai-service
success "AI Service rebuilt"

# Step 5: Build dashboard
info "Step 5/10: Building dashboard..."
cd dashboard
npm run build
if [ $? -ne 0 ]; then
    error "Dashboard build failed"
    exit 1
fi
success "Dashboard built successfully"
cd ..

# Step 6: Stop services gracefully
info "Step 6/10: Stopping services..."
docker-compose down
pm2 stop rtgs-dashboard 2>/dev/null || true
success "Services stopped"

# Step 7: Start Docker services
info "Step 7/10: Starting Docker services..."
docker-compose up -d
sleep 30  # Wait for services to initialize
success "Docker services started"

# Step 8: Import and activate n8n workflows
info "Step 8/10: Configuring n8n workflows..."

# Wait for n8n to be ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec -u node ai-assist-n8n n8n list:workflow &>/dev/null; then
        break
    fi
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    error "n8n failed to start"
    exit 1
fi

# Clean up old workflows
python3 final_cleanup_dashboard.py
success "n8n workflows configured"

# Step 9: Start dashboard
info "Step 9/10: Starting dashboard..."
cd dashboard

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    warning "PM2 not installed, installing..."
    npm install -g pm2
fi

# Start with PM2
pm2 delete rtgs-dashboard 2>/dev/null || true
pm2 start npm --name "rtgs-dashboard" -- start
pm2 save
success "Dashboard started with PM2"
cd ..

# Step 10: Health checks
info "Step 10/10: Running health checks..."
sleep 10

# Check Docker services
if ! docker ps | grep -q "ai-assist-n8n"; then
    error "n8n container not running"
    exit 1
fi

if ! docker ps | grep -q "ai-assist-ai-service"; then
    error "AI service container not running"
    exit 1
fi

# Check dashboard
if ! pm2 list | grep -q "rtgs-dashboard.*online"; then
    error "Dashboard not running"
    exit 1
fi

# Check n8n API
if ! curl -s -u admin:admin123 http://localhost:5678/healthz &>/dev/null; then
    warning "n8n health check failed"
fi

# Check AI service
if ! curl -s http://localhost:8000/health &>/dev/null; then
    warning "AI service health check failed"
fi

success "All health checks passed"

# Deployment summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              DEPLOYMENT COMPLETED SUCCESSFULLY             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
info "Deployment Summary:"
echo "  • Dashboard: http://localhost:3000"
echo "  • n8n Admin: http://localhost:5678"
echo "  • AI Service: http://localhost:8000"
echo "  • Backup: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "  • Logs: $LOG_FILE"
echo ""
info "Next Steps:"
echo "  1. Configure SSL certificate (if not done)"
echo "  2. Set up Telegram webhook"
echo "  3. Configure monitoring"
echo "  4. Run smoke tests"
echo ""
success "Deployment completed at $(date +'%Y-%m-%d %H:%M:%S')"
