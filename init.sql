-- Database initialization script for Task Manager
USE taskdb;

-- Create the task table (Flask-SQLAlchemy will handle this, but this is a backup)
CREATE TABLE IF NOT EXISTS task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample data for testing
INSERT INTO task (title, description, completed) VALUES
('Welcome Task', 'This is a sample task to get you started!', FALSE),
('Learn Docker', 'Master containerization with Docker', FALSE),
('Setup CI/CD', 'Configure Jenkins pipeline for automated deployment', TRUE);

-- Grant permissions
GRANT ALL PRIVILEGES ON taskdb.* TO 'appuser'@'%';
FLUSH PRIVILEGES; 