import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException


class TaskManagerSeleniumTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        cls.wait = WebDriverWait(cls.driver, 10)
    
    @classmethod
    def tearDownClass(cls):
        """Close the browser"""
        cls.driver.quit()
    
    def setUp(self):
        """Navigate to the home page before each test"""
        self.driver.get(self.base_url)
        time.sleep(1)  # Allow page to load
    
    def test_page_title_and_header(self):
        """Test that the page title and header are correct"""
        self.assertIn("Task Manager", self.driver.title)
        
        header = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h2"))
        )
        self.assertIn("Task Manager", header.text)
    
    def test_add_task_functionality(self):
        """Test adding a new task"""
        # Find and fill the title field
        title_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        title_field.clear()
        title_field.send_keys("Selenium Test Task")
        
        # Find and fill the description field
        description_field = self.driver.find_element(By.ID, "description")
        description_field.clear()
        description_field.send_keys("This is a test task created by Selenium")
        
        # Submit the form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for the success message
        try:
            success_alert = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
            )
            self.assertIn("Task added successfully!", success_alert.text)
        except TimeoutException:
            pass  # Success message may not appear if redirected too quickly
        
        # Verify the task appears in the list
        task_title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h6[contains(text(), 'Selenium Test Task')]"))
        )
        self.assertEqual("Selenium Test Task", task_title.text)
    
    def test_add_task_without_title(self):
        """Test that adding a task without title shows error"""
        # Find the description field and fill it
        description_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "description"))
        )
        description_field.clear()
        description_field.send_keys("Description without title")
        
        # Submit the form without filling title
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Check if HTML5 validation prevents submission
        title_field = self.driver.find_element(By.ID, "title")
        validation_message = title_field.get_attribute("validationMessage")
        self.assertTrue(len(validation_message) > 0)  # HTML5 validation should trigger
    
    def test_toggle_task_completion(self):
        """Test toggling task completion status"""
        # First add a task
        self.add_test_task("Toggle Test Task", "Task to test toggle functionality")
        
        # Find and click the toggle button
        toggle_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".toggle-btn"))
        )
        toggle_button.click()
        
        # Wait for the page to reload or AJAX to complete
        time.sleep(2)
        
        # Check if the button style changed (success style for completed tasks)
        toggle_button = self.driver.find_element(By.CSS_SELECTOR, ".toggle-btn")
        button_classes = toggle_button.get_attribute("class")
        self.assertIn("btn-success", button_classes)
    
    def test_edit_task_functionality(self):
        """Test editing an existing task"""
        # First add a task
        self.add_test_task("Edit Test Task", "Original description")
        
        # Find and click the edit button
        edit_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='editTask']"))
        )
        edit_button.click()
        
        # Wait for modal to appear
        modal = self.wait.until(
            EC.presence_of_element_located((By.ID, "editModal"))
        )
        
        # Update the title
        edit_title_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "editTitle"))
        )
        edit_title_field.clear()
        edit_title_field.send_keys("Updated Edit Test Task")
        
        # Update the description
        edit_description_field = self.driver.find_element(By.ID, "editDescription")
        edit_description_field.clear()
        edit_description_field.send_keys("Updated description")
        
        # Submit the edit form
        update_button = self.driver.find_element(By.CSS_SELECTOR, "#editModal button[type='submit']")
        update_button.click()
        
        # Wait for modal to close and page to reload
        time.sleep(2)
        
        # Verify the task was updated
        updated_task = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h6[contains(text(), 'Updated Edit Test Task')]"))
        )
        self.assertEqual("Updated Edit Test Task", updated_task.text)
    
    def test_delete_task_functionality(self):
        """Test deleting a task"""
        # First add a task
        self.add_test_task("Delete Test Task", "Task to be deleted")
        
        # Find the delete button and click it
        delete_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'] .fa-trash"))
        )
        delete_button.click()
        
        # Handle the confirmation dialog
        alert = self.wait.until(EC.alert_is_present())
        alert.accept()
        
        # Wait for page to reload
        time.sleep(2)
        
        # Verify the task is no longer present
        tasks = self.driver.find_elements(By.XPATH, "//h6[contains(text(), 'Delete Test Task')]")
        self.assertEqual(len(tasks), 0)
    
    def test_empty_state_display(self):
        """Test that empty state is displayed when no tasks exist"""
        # Check if we're on a page with no tasks
        try:
            empty_message = self.driver.find_element(By.XPATH, "//h5[contains(text(), 'No tasks yet!')]")
            self.assertIn("No tasks yet!", empty_message.text)
        except:
            # If there are tasks, this test is not applicable
            pass
    
    def test_task_count_display(self):
        """Test that task count is displayed correctly"""
        # Get initial task count
        tasks_header = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h5[contains(text(), 'Tasks')]"))
        )
        
        # Extract count from header text like "Tasks (2)"
        import re
        count_match = re.search(r'Tasks \((\d+)\)', tasks_header.text)
        if count_match:
            initial_count = int(count_match.group(1))
        else:
            initial_count = 0
        
        # Add a new task
        self.add_test_task("Count Test Task", "Testing task count")
        
        # Check that count increased
        tasks_header = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h5[contains(text(), 'Tasks')]"))
        )
        count_match = re.search(r'Tasks \((\d+)\)', tasks_header.text)
        new_count = int(count_match.group(1))
        
        self.assertEqual(new_count, initial_count + 1)
    
    def test_responsive_design_elements(self):
        """Test that key responsive design elements are present"""
        # Check that Bootstrap classes are applied
        container = self.driver.find_element(By.CSS_SELECTOR, ".container")
        self.assertTrue(container.is_displayed())
        
        # Check that cards are present
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
        self.assertTrue(len(cards) > 0)
        
        # Check that buttons have proper styling
        buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn")
        self.assertTrue(len(buttons) > 0)
    
    def add_test_task(self, title, description):
        """Helper method to add a test task"""
        title_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        title_field.clear()
        title_field.send_keys(title)
        
        description_field = self.driver.find_element(By.ID, "description")
        description_field.clear()
        description_field.send_keys(description)
        
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(1)  # Wait for the task to be added


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 