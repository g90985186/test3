#!/bin/bash

echo "🔧 Fixing PostgreSQL Database Permissions"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🗄️ Setting up PostgreSQL database and permissions..."

# Method 1: Fix permissions for existing database
echo "Attempting to fix permissions for existing database..."

sudo -u postgres psql << 'EOF'
-- Drop and recreate database with proper permissions
DROP DATABASE IF EXISTS cvedb;
DROP USER IF EXISTS cveuser;

-- Create new user with proper permissions
CREATE USER cveuser WITH PASSWORD 'cvepassword';
ALTER USER cveuser CREATEDB;

-- Create database owned by the user
CREATE DATABASE cvedb OWNER cveuser;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE cvedb TO cveuser;

-- Connect to the database and grant schema permissions
\c cvedb;

-- Grant permissions on public schema
GRANT ALL ON SCHEMA public TO cveuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cveuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cveuser;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cveuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cveuser;

-- Show user permissions
\du cveuser;

\q
EOF

if [ $? -eq 0 ]; then
    print_status "Database permissions fixed successfully"
else
    print_error "Failed to fix database permissions automatically"
    echo ""
    print_warning "Manual fix required. Run these commands:"
    echo "sudo -u postgres psql"
    echo "DROP DATABASE IF EXISTS cvedb;"
    echo "DROP USER IF EXISTS cveuser;"
    echo "CREATE USER cveuser WITH PASSWORD 'cvepassword';"
    echo "ALTER USER cveuser CREATEDB;"
    echo "CREATE DATABASE cvedb OWNER cveuser;"
    echo "GRANT ALL PRIVILEGES ON DATABASE cvedb TO cveuser;"
    echo "\\c cvedb;"
    echo "GRANT ALL ON SCHEMA public TO cveuser;"
    echo "\\q"
fi

# Test the connection
echo ""
echo "🧪 Testing database connection..."

if PGPASSWORD=cvepassword psql -h localhost -U cveuser -d cvedb -c "SELECT version();" >/dev/null 2>&1; then
    print_status "Database connection test successful"
else
    print_error "Database connection test failed"
fi

echo ""
print_status "Database fix completed!"
