import unittest
import json
import os
import tempfile
from app import app, db, Task


class TaskManagerTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test database and client"""
        self.db_fd, app.config['DATABASE_URL'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
    
    def test_index_page(self):
        """Test the main index page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task Manager', response.data)
    
    def test_add_task(self):
        """Test adding a new task"""
        response = self.app.post('/add', data={
            'title': 'Test Task',
            'description': 'Test Description'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task added successfully!', response.data)
        
        # Verify task was added to database
        task = Task.query.filter_by(title='Test Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.description, 'Test Description')
        self.assertFalse(task.completed)
    
    def test_add_task_without_title(self):
        """Test adding task without title fails"""
        response = self.app.post('/add', data={
            'title': '',
            'description': 'Test Description'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Title is required!', response.data)
    
    def test_update_task(self):
        """Test updating an existing task"""
        # First create a task
        task = Task(title='Original Title', description='Original Description')
        db.session.add(task)
        db.session.commit()
        
        # Update the task
        response = self.app.post(f'/update/{task.id}', data={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'completed': 'on'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task updated successfully!', response.data)
        
        # Verify task was updated
        updated_task = Task.query.get(task.id)
        self.assertEqual(updated_task.title, 'Updated Title')
        self.assertEqual(updated_task.description, 'Updated Description')
        self.assertTrue(updated_task.completed)
    
    def test_delete_task(self):
        """Test deleting a task"""
        # First create a task
        task = Task(title='Task to Delete', description='Will be deleted')
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
        # Delete the task
        response = self.app.post(f'/delete/{task_id}', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task deleted successfully!', response.data)
        
        # Verify task was deleted
        deleted_task = Task.query.get(task_id)
        self.assertIsNone(deleted_task)
    
    def test_toggle_task(self):
        """Test toggling task completion status"""
        # Create a task
        task = Task(title='Toggle Task', completed=False)
        db.session.add(task)
        db.session.commit()
        
        # Toggle to completed
        response = self.app.post(f'/toggle/{task.id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['completed'])
        
        # Verify in database
        toggled_task = Task.query.get(task.id)
        self.assertTrue(toggled_task.completed)
        
        # Toggle back to incomplete
        response = self.app.post(f'/toggle/{task.id}')
        data = json.loads(response.data)
        self.assertFalse(data['completed'])
    
    def test_get_tasks_api(self):
        """Test API endpoint for getting all tasks"""
        # Create test tasks
        task1 = Task(title='Task 1', description='Description 1')
        task2 = Task(title='Task 2', description='Description 2', completed=True)
        
        db.session.add(task1)
        db.session.add(task2)
        db.session.commit()
        
        # Test API endpoint
        response = self.app.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Task 1')
        self.assertEqual(data[1]['title'], 'Task 2')
        self.assertTrue(data[1]['completed'])
    
    def test_create_task_api(self):
        """Test API endpoint for creating tasks"""
        task_data = {
            'title': 'API Task',
            'description': 'Created via API'
        }
        
        response = self.app.post('/api/tasks',
                               data=json.dumps(task_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'API Task')
        self.assertEqual(data['description'], 'Created via API')
        self.assertFalse(data['completed'])
        
        # Verify in database
        task = Task.query.filter_by(title='API Task').first()
        self.assertIsNotNone(task)
    
    def test_task_model_to_dict(self):
        """Test Task model to_dict method"""
        task = Task(title='Test Task', description='Test Description')
        db.session.add(task)
        db.session.commit()
        
        task_dict = task.to_dict()
        self.assertEqual(task_dict['title'], 'Test Task')
        self.assertEqual(task_dict['description'], 'Test Description')
        self.assertFalse(task_dict['completed'])
        self.assertIn('created_at', task_dict)
        self.assertIn('id', task_dict)
    
    def test_404_for_nonexistent_task(self):
        """Test 404 error for operations on non-existent tasks"""
        response = self.app.post('/update/999', data={
            'title': 'Updated',
            'description': 'Updated'
        })
        self.assertEqual(response.status_code, 404)
        
        response = self.app.post('/delete/999')
        self.assertEqual(response.status_code, 404)
        
        response = self.app.post('/toggle/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main() 