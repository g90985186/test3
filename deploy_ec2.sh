#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Start and enable services
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create application directory
sudo mkdir -p /opt/cve-platform
sudo chown ubuntu:ubuntu /opt/cve-platform

# Clone the repository
cd /opt/cve-platform
git clone https://github.com/g90985186/fcxgdfsgsdfgsd.git .

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create and configure PostgreSQL database
sudo -u postgres psql -c "CREATE DATABASE cve_platform;"
sudo -u postgres psql -c "CREATE USER cve_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cve_platform TO cve_user;"

# Create .env file
cat > .env << EOL
DATABASE_URL=postgresql://cve_user:your_secure_password@localhost/cve_platform
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
OLLAMA_API_BASE=http://localhost:11434
EOL

# Set up Nginx configuration
sudo tee /etc/nginx/sites-available/cve-platform << EOL
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOL

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/cve-platform /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Create systemd service
sudo tee /etc/systemd/system/cve-platform.service << EOL
[Unit]
Description=CVE Analysis Platform
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/cve-platform
Environment="PATH=/opt/cve-platform/venv/bin"
ExecStart=/opt/cve-platform/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
EOL

# Start the application
sudo systemctl daemon-reload
sudo systemctl start cve-platform
sudo systemctl enable cve-platform

# Install and configure Ollama
curl https://ollama.ai/install.sh | sh
ollama pull llama2
ollama pull codellama

echo "Deployment completed! The application should be running at http://your-ec2-ip" 
