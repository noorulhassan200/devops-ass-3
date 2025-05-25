# Task Manager - Flask Web Application

A complete Flask web application with CRUD functionality, MySQL database, Docker containerization, and comprehensive CI/CD pipeline using Jenkins.

## 🚀 Features

- **Modern Web Interface**: Beautiful, responsive UI built with Bootstrap 5
- **Full CRUD Operations**: Create, Read, Update, Delete tasks
- **MySQL Database**: Persistent data storage with MySQL 8.0
- **RESTful API**: API endpoints for external integrations
- **Containerized**: Docker and Docker Compose ready
- **Comprehensive Testing**: Unit tests and Selenium end-to-end tests
- **CI/CD Pipeline**: Complete Jenkins pipeline with 5 stages

## 📋 Required Libraries

The application uses the following Python libraries:

### Flask Application Dependencies:
- `Flask==2.3.3` - Web framework
- `Flask-SQLAlchemy==3.0.5` - Database ORM
- `Flask-Migrate==4.0.5` - Database migrations
- `PyMySQL==1.1.0` - MySQL database driver
- `cryptography==41.0.4` - Security and encryption

### Testing Dependencies:
- `selenium==4.15.0` - Web browser automation
- `unittest-xml-reporting==3.2.0` - XML test reports

### Development Dependencies:
- `flake8` - Code linting
- `coverage` - Test coverage reporting

## 🏗️ Project Structure

```
├── app.py                      # Main Flask application
├── test_app.py                 # Unit tests
├── templates/
│   └── index.html             # Main UI template
├── selenium_tests/
│   ├── test_selenium.py       # Selenium E2E tests
│   └── Dockerfile            # Selenium test container
├── Dockerfile                 # Main app container
├── docker-compose.yml         # Multi-container orchestration
├── init.sql                   # Database initialization
├── Jenkinsfile               # CI/CD pipeline
└── README.md                 # This file
```

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- MySQL 8.0 (if running locally)

### Quick Start with Docker Compose

1. **Clone and run the application:**
```bash
git clone <repository-url>
cd task-manager
docker-compose up -d
```

2. **Access the application:**
- Web Interface: http://localhost:5000
- MySQL Database: localhost:3306

3. **Stop the application:**
```bash
docker-compose down -v
```

### Manual Setup (Without Docker)

1. **Install dependencies:**
```bash
pip install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 Flask-Migrate==4.0.5 PyMySQL==1.1.0 cryptography==41.0.4
```

2. **Setup MySQL database:**
```sql
CREATE DATABASE taskdb;
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'apppassword';
GRANT ALL PRIVILEGES ON taskdb.* TO 'appuser'@'localhost';
```

3. **Set environment variables:**
```bash
export DATABASE_URL="mysql+pymysql://appuser:apppassword@localhost:3306/taskdb"
export FLASK_APP=app.py
```

4. **Run the application:**
```bash
python app.py
```

## 🧪 Testing

### Unit Tests
```bash
python -m unittest test_app.py -v
```

### Selenium Tests (requires running application)
```bash
cd selenium_tests
pip install selenium==4.15.0
python test_selenium.py
```

### Run Tests with Docker
```bash
# Run Selenium tests
docker-compose --profile testing up selenium-tests
```

## 🚀 CI/CD Pipeline

The Jenkins pipeline includes 5 comprehensive stages:

### 1. **Code Linting Stage**
- Uses `flake8` for Python code quality checks
- Enforces PEP 8 standards with custom configurations
- Generates linting reports

### 2. **Code Build Stage**
- Builds Docker images for the Flask application
- Builds Docker images for Selenium tests
- Tags images with build numbers

### 3. **Unit Testing Stage**
- Sets up Python virtual environment
- Runs comprehensive unit tests
- Generates code coverage reports
- Archives test results

### 4. **Containerized Deployment Stage**
- Deploys MySQL database container
- Deploys Flask application container
- Performs health checks
- Verifies application accessibility

### 5. **Selenium Testing Stage**
- Runs end-to-end browser tests
- Tests complete user workflows
- Captures test results and logs

## 🐳 Docker Configuration

### Main Application Container (`Dockerfile`)
- Based on Python 3.9 slim
- Includes MySQL client libraries
- Runs as non-root user
- Includes health checks

### Selenium Test Container (`selenium_tests/Dockerfile`)
- Includes Chrome and ChromeDriver
- Configured for headless testing
- Optimized for CI/CD environments

### Docker Compose Services
- **mysql**: MySQL 8.0 database
- **web**: Flask application
- **selenium-tests**: E2E test runner

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: MySQL connection string
- `FLASK_ENV`: Flask environment (production/development)
- `BASE_URL`: Application URL for Selenium tests

### Database Configuration
- **Database**: `taskdb`
- **Default User**: `root` / `password`
- **App User**: `appuser` / `apppassword`

## 📊 API Endpoints

### Web Routes
- `GET /` - Main application interface
- `POST /add` - Add new task
- `POST /update/<id>` - Update existing task
- `POST /delete/<id>` - Delete task
- `POST /toggle/<id>` - Toggle task completion

### API Routes
- `GET /api/tasks` - Get all tasks (JSON)
- `POST /api/tasks` - Create new task (JSON)

## 🔍 Monitoring and Logs

### Health Checks
- Application health endpoint: `GET /`
- MySQL health check via `mysqladmin ping`

### Logging
- Application logs via Docker logs
- Jenkins pipeline logs and artifacts
- Test results and coverage reports

## 🚀 Jenkins Setup

1. **Create a new Pipeline job in Jenkins**
2. **Configure Pipeline from SCM:**
   - Repository URL: Your Git repository
   - Script Path: `Jenkinsfile`
3. **Required Jenkins Plugins:**
   - Docker Pipeline
   - Pipeline Stage View
   - HTML Publisher (for coverage reports)

### Pipeline Environment Variables
Configure these in Jenkins or the Jenkinsfile:
- `DOCKER_IMAGE`: Docker image name
- `MYSQL_ROOT_PASSWORD`: MySQL root password
- `COMPOSE_PROJECT_NAME`: Docker Compose project name

## 🛡️ Security Considerations

- Application runs as non-root user in containers
- Database credentials should be stored in Jenkins secrets
- Use environment-specific configuration files
- Regular security updates for base images

## 📈 Performance Features

- Database connection pooling via SQLAlchemy
- Optimized Docker images with minimal attack surface
- Health checks for reliable deployments
- Resource limits in Docker Compose

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   - Verify MySQL container is running
   - Check connection string format
   - Ensure database and user exist

2. **Selenium Test Failures:**
   - Verify application is accessible
   - Check Chrome/ChromeDriver compatibility
   - Increase wait times for slow environments

3. **Docker Build Failures:**
   - Check available disk space
   - Verify internet connectivity for package downloads
   - Review Docker daemon logs

### Debug Commands
```bash
# Check container logs
docker-compose logs web
docker-compose logs mysql

# Test database connectivity
docker-compose exec mysql mysql -uroot -ppassword -e "SHOW DATABASES;"

# Test application endpoint
curl -f http://localhost:5000/api/tasks
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests locally
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Happy Coding! 🎉** 