from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration with fallback to SQLite for local development
def get_database_uri():
    """Get database URI with fallback to SQLite for local development"""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url
    
    # Try MySQL first, fallback to SQLite
    mysql_uri = 'mysql+pymysql://root:password@localhost:3306/taskdb'
    try:
        # Test MySQL connection
        import pymysql
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='password',
            database='taskdb'
        )
        connection.close()
        return mysql_uri
    except:
        # Fallback to SQLite for local development
        return 'sqlite:///tasks.db'

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }

# Routes
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    
    if title:
        task = Task(title=title, description=description)
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    else:
        flash('Title is required!', 'error')
    
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.title = request.form.get('title', task.title)
    task.description = request.form.get('description', task.description)
    task.completed = bool(request.form.get('completed'))
    
    db.session.commit()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return jsonify({'status': 'success', 'completed': task.completed})

# API Routes for testing
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task_api():
    data = request.get_json()
    task = Task(title=data['title'], description=data.get('description', ''))
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Add sample data if running with SQLite
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            if Task.query.count() == 0:
                sample_tasks = [
                    Task(title='Welcome Task', description='This is a sample task to get you started!'),
                    Task(title='Learn Docker', description='Master containerization with Docker'),
                    Task(title='Setup CI/CD', description='Configure Jenkins pipeline for automated deployment', completed=True)
                ]
                for task in sample_tasks:
                    db.session.add(task)
                db.session.commit()
                print("Sample data added to SQLite database")
    
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(host='0.0.0.0', port=5000, debug=True) 