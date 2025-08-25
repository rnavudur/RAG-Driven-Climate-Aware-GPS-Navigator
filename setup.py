#!/usr/bin/env python3
"""
Setup script for Climate-Aware GPS Navigator
This script helps set up the development environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed."""
    print("🔍 Checking system requirements...")
    
    requirements = {
        'docker': 'docker --version',
        'docker-compose': 'docker-compose --version',
        'python': 'python --version',
        'pip': 'pip --version'
    }
    
    missing = []
    for tool, command in requirements.items():
        if shutil.which(tool) is None:
            missing.append(tool)
        else:
            print(f"✅ {tool} is installed")
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        print("Please install the missing tools and run this script again.")
        return False
    
    return True

def create_env_file():
    """Create .env file from template."""
    print("📝 Creating environment file...")
    
    env_template = Path("env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists, skipping...")
        return True
    
    if not env_template.exists():
        print("❌ env.example not found")
        return False
    
    try:
        shutil.copy(env_template, env_file)
        print("✅ .env file created from template")
        print("⚠️  Please edit .env with your actual API keys and database credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def install_python_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    return True

def start_services():
    """Start Docker services."""
    print("🐳 Starting Docker services...")
    
    if not run_command("docker-compose up -d", "Starting Docker containers"):
        return False
    
    print("⏳ Waiting for services to be ready...")
    print("   This may take a few minutes on first run...")
    
    return True

def check_services():
    """Check if services are running."""
    print("🔍 Checking service status...")
    
    services = ['postgres', 'redis', 'app']
    all_healthy = True
    
    for service in services:
        if not run_command(f"docker-compose ps {service}", f"Checking {service}"):
            all_healthy = False
    
    return all_healthy

def run_migrations():
    """Run database migrations."""
    print("🗄️  Setting up database...")
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    if not run_command("docker-compose exec postgres pg_isready -U climate_user -d climate_gps", "Checking database readiness"):
        print("⚠️  Database not ready yet, migrations will need to be run manually")
        return False
    
    print("✅ Database is ready")
    return True

def main():
    """Main setup function."""
    print("🚀 Climate-Aware GPS Navigator Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Start services
    if not start_services():
        sys.exit(1)
    
    # Check services
    if not check_services():
        print("⚠️  Some services may not be running properly")
    
    # Run migrations
    if not run_migrations():
        print("⚠️  Database setup incomplete")
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Access the application at http://localhost:8000")
    print("3. View API documentation at http://localhost:8000/docs")
    print("4. Access pgAdmin at http://localhost:5050 (admin@climategps.com / admin)")
    print("\n🔧 Useful commands:")
    print("   docker-compose logs -f app          # View application logs")
    print("   docker-compose down                 # Stop all services")
    print("   docker-compose up -d                # Start all services")
    print("   docker-compose restart app          # Restart application")

if __name__ == "__main__":
    main() 