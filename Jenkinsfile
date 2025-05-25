pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'task-manager-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        COMPOSE_PROJECT_NAME = "taskmanager-${BUILD_NUMBER}"
        MYSQL_ROOT_PASSWORD = 'password'
        DATABASE_URL = "mysql+pymysql://root:${MYSQL_ROOT_PASSWORD}@mysql:3306/taskdb"
    }
    
    stages {
        stage('Code Linting') {
            steps {
                echo 'Starting Code Linting Stage...'
                script {
                    // Install flake8 and run linting
                    sh '''
                        python3 -m venv test_env
                        source test_env/bin/activate
                        pip install flake8
                        echo "Running flake8 linting on Python files..."
                        python3 -m flake8 app.py test_app.py --max-line-length=88 --ignore=E203,W503 || true
                        echo "Linting selenium test files..."
                        python3 -m flake8 selenium_tests/test_selenium.py --max-line-length=88 --ignore=E203,W503 || true
                    '''
                }
                echo 'Code Linting Stage Completed!'
            }
            post {
                always {
                    // Archive linting results
                    sh 'python3 -m flake8 app.py test_app.py selenium_tests/test_selenium.py --format=pylint --output-file=flake8_report.txt || true'
                    archiveArtifacts artifacts: 'flake8_report.txt', allowEmptyArchive: true
                }
            }
        }
        
        stage('Code Build') {
            steps {
                echo 'Starting Code Build Stage...'
                script {
                    // Build Docker images
                    sh '''
                        echo "Building Flask application Docker image..."
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                        
                        echo "Building Selenium test Docker image..."
                        docker build -t selenium-tests:${DOCKER_TAG} ./selenium_tests/
                        docker tag selenium-tests:${DOCKER_TAG} selenium-tests:latest
                        
                        echo "Docker images built successfully!"
                        docker images | grep -E "(${DOCKER_IMAGE}|selenium-tests)"
                    '''
                }
                echo 'Code Build Stage Completed!'
            }
            post {
                always {
                    // Clean up intermediate build artifacts
                    sh 'docker system prune -f --filter label=stage=build || true'
                }
            }
        }
        
        stage('Unit Testing') {
            steps {
                echo 'Starting Unit Testing Stage...'
                script {
                    sh '''
                        echo "Setting up Python virtual environment for unit tests..."
                        python3 -m venv test_env
                        source test_env/bin/activate
                        
                        echo "Installing test dependencies..."
                        pip install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 Flask-Migrate==4.0.5 PyMySQL==1.1.0 cryptography==41.0.4
                        
                        echo "Running unit tests..."
                        python -m unittest test_app.py -v
                        
                        echo "Generating test coverage report..."
                        pip install coverage
                        coverage run -m unittest test_app.py
                        coverage report
                        coverage html -d coverage_html_report
                        
                        deactivate
                    '''
                }
                echo 'Unit Testing Stage Completed!'
            }
            post {
                always {
                    // Archive test results and coverage reports
                    archiveArtifacts artifacts: 'coverage_html_report/**', allowEmptyArchive: true
                    // Clean up test environment
                    sh 'rm -rf test_env || true'
                }
            }
        }
        
        stage('Containerized Deployment') {
            steps {
                echo 'Starting Containerized Deployment Stage...'
                script {
                    sh '''
                        echo "Stopping any existing containers..."
                        docker-compose -p ${COMPOSE_PROJECT_NAME} down -v || true
                        
                        echo "Starting MySQL database..."
                        docker-compose -p ${COMPOSE_PROJECT_NAME} up -d mysql
                        
                        echo "Waiting for MySQL to be ready..."
                        sleep 30
                        
                        echo "Starting Flask application..."
                        docker-compose -p ${COMPOSE_PROJECT_NAME} up -d web
                        
                        echo "Waiting for application to be ready..."
                        sleep 20
                        
                        echo "Checking application health..."
                        timeout 60 bash -c 'until curl -f http://localhost:5000/; do echo "Waiting for app..."; sleep 2; done'
                        
                        echo "Application deployed successfully!"
                        docker-compose -p ${COMPOSE_PROJECT_NAME} ps
                    '''
                }
                echo 'Containerized Deployment Stage Completed!'
            }
            post {
                failure {
                    // Gather logs on deployment failure
                    sh '''
                        echo "Deployment failed, gathering logs..."
                        docker-compose -p ${COMPOSE_PROJECT_NAME} logs web > deployment_logs.txt 2>&1 || true
                        docker-compose -p ${COMPOSE_PROJECT_NAME} logs mysql >> deployment_logs.txt 2>&1 || true
                    '''
                    archiveArtifacts artifacts: 'deployment_logs.txt', allowEmptyArchive: true
                }
            }
        }
        
        stage('Selenium Testing') {
            steps {
                echo 'Starting Selenium Testing Stage...'
                script {
                    sh '''
                        echo "Verifying application is running..."
                        curl -f http://localhost:5000/ || (echo "Application not accessible!" && exit 1)
                        
                        echo "Creating test results directory..."
                        mkdir -p test_results
                        
                        echo "Running Selenium tests..."
                        docker run --rm \
                            --network ${COMPOSE_PROJECT_NAME}_app-network \
                            -e BASE_URL=http://web:5000 \
                            -v $(pwd)/test_results:/app/test_results \
                            selenium-tests:${DOCKER_TAG} \
                            python -m unittest test_selenium.py -v
                        
                        echo "Selenium tests completed successfully!"
                    '''
                }
                echo 'Selenium Testing Stage Completed!'
            }
            post {
                always {
                    // Archive Selenium test results
                    archiveArtifacts artifacts: 'test_results/**', allowEmptyArchive: true
                }
                failure {
                    // Capture screenshots and logs on test failure
                    sh '''
                        echo "Selenium tests failed, gathering additional logs..."
                        docker-compose -p ${COMPOSE_PROJECT_NAME} logs web > selenium_failure_logs.txt 2>&1 || true
                    '''
                    archiveArtifacts artifacts: 'selenium_failure_logs.txt', allowEmptyArchive: true
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed!'
            script {
                // Clean up Docker containers and networks
                sh '''
                    echo "Cleaning up Docker resources..."
                    docker-compose -p ${COMPOSE_PROJECT_NAME} down -v --remove-orphans || true
                    docker system prune -f --filter label=stage=test || true
                '''
            }
        }
        
        success {
            echo 'Pipeline completed successfully!'
            // You can add notifications here (email, Slack, etc.)
            script {
                sh '''
                    echo "All stages passed successfully!"
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    echo "Timestamp: $(date)"
                '''
            }
        }
        
        failure {
            echo 'Pipeline failed!'
            // You can add failure notifications here
            script {
                sh '''
                    echo "Pipeline failed at stage: ${env.STAGE_NAME}"
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Timestamp: $(date)"
                    echo "Please check the logs for more details."
                '''
            }
        }
        
        cleanup {
            echo 'Performing final cleanup...'
            // Clean up workspace if needed
            deleteDir()
        }
    }
} 