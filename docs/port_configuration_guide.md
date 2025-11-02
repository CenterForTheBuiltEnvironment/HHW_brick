# Port Configuration Guide

## 📋 Port Configuration Overview

### 🔌 Basic Port Configuration
```yaml
port: 8080  # Application listening port number
```

### 🎯 Port Usage Details

#### 1. **Web Interface Access**
- **Purpose**: Provides browser-based user interface
- **Features**:
  - CSV data upload and conversion
  - Brick model visualization
  - System status monitoring
  - Configuration management
- **Access**: `http://localhost:8080`

#### 2. **API Services**
```python
# Example API endpoints
GET  /status          # Get system status
POST /convert         # Convert CSV data
GET  /config          # Get configuration info
POST /deploy          # Deploy application
```

#### 3. **Docker Container Deployment**
```yaml
docker:
  ports:
    - "8080:8080"     # host_port:container_port
```
- **Host Port (8080)**: External access port
- **Container Port (8080)**: Application port inside container
- **Port Mapping**: Allows external access to container service via host_ip:8080

#### 4. **Kubernetes Cluster Deployment**
```yaml
kubernetes:
  service_type: "LoadBalancer"
  # Automatically creates Service using port configuration
```
- **Pod Port**: Application listening port inside container
- **Service Port**: Cluster-internal service communication port
- **LoadBalancer**: External service exposure port

## 🔧 Port Usage in Different Deployment Modes

### Local Development Mode
```bash
# Start application
python examples/web_app_example.py --port 8080

# Access URL
http://localhost:8080
```

### Docker Container Mode
```bash
# Build and run
docker build -t hhw-brick-app .
docker run -p 8080:8080 hhw-brick-app

# Access URL
http://localhost:8080
```

### Kubernetes Cluster Mode
```bash
# Deploy to cluster
kubectl apply -f k8s/

# Access via Service
kubectl port-forward service/hhws-app-service 8080:8080
```

## 🌐 Real-World Application Scenarios

### Scenario 1: Data Center Monitoring
- **Port**: 8080
- **Function**: Real-time HHWS system status display
- **Users**: Operations staff monitoring via browser

### Scenario 2: Data Conversion Service
- **Port**: 8080
- **Function**: Receives CSV files, returns Brick format data
- **Users**: Other systems calling via API

### Scenario 3: Multi-Tenant Deployment
- **Ports**: 8080, 8081, 8082...
- **Function**: Deploy separate instances for different buildings
- **Users**: Each building has its own management interface

## ⚙️ Port Configuration Best Practices

### 1. Port Selection Principles
- **Avoid Conflicts**: Do not use system reserved ports (0-1023)
- **Enterprise Standards**: Follow company port allocation standards
- **Firewall**: Ensure selected port is open in firewall

### 2. Security Considerations
- **Internal Network**: Recommend exposing only on internal network in production
- **HTTPS**: Use SSL/TLS encryption in production
- **Authentication**: Add user authentication and access control

### 3. Monitoring and Logging
- **Health Checks**: Configure port health checks
- **Access Logs**: Record all access requests
- **Performance Monitoring**: Monitor port response times

## 🚀 Quick Port Configuration Testing

### Test Web Interface
```bash
# Start test server
python examples/web_app_example.py --port 8080 --debug

# Open in browser
http://localhost:8080
```

### Test API Endpoints
```bash
# Check service status
curl http://localhost:8080/status

# Get configuration info
curl http://localhost:8080/config
```
