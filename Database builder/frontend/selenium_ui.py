from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class DatabaseCreatorUI:
    """Selenium-based UI for Automated Database Creator"""
    
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
    
    def start(self):
        """Start the application"""
        self.driver.get(self.base_url)
        time.sleep(2)
    
    def upload_file(self, file_path):
        """Upload data file"""
        file_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "file-upload"))
        )
        file_input.send_keys(file_path)
        
        # Wait for analysis to complete
        time.sleep(3)
        return self.get_file_analysis()
    
    def select_database(self, db_type):
        """Select database system"""
        db_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "database-select"))
        )
        Select(db_select).select_by_value(db_type)
        time.sleep(1)
    
    def enter_credentials(self, credentials):
        """Enter database credentials"""
        for key, value in credentials.items():
            field = self.driver.find_element(By.ID, f"cred-{key}")
            field.clear()
            field.send_keys(value)
        
        time.sleep(1)
    
    def enter_openrouter_key(self, api_key, model):
        """Enter OpenRouter API key and model"""
        key_field = self.driver.find_element(By.ID, "openrouter-key")
        key_field.send_keys(api_key)
        
        model_field = self.driver.find_element(By.ID, "model-select")
        model_field.send_keys(model)
        
        time.sleep(1)
    
    def design_schema(self):
        """Trigger schema design"""
        design_btn = self.driver.find_element(By.ID, "design-schema-btn")
        design_btn.click()
        
        # Wait for schema design to complete
        time.sleep(5)
        return self.get_schema_preview()
    
    def deploy_schema(self):
        """Deploy schema to database"""
        deploy_btn = self.driver.find_element(By.ID, "deploy-btn")
        deploy_btn.click()
        
        # Wait for deployment
        time.sleep(5)
        return self.get_deployment_status()
    
    def get_file_analysis(self):
        """Get file analysis results"""
        analysis_div = self.driver.find_element(By.ID, "analysis-results")
        return analysis_div.text
    
    def get_schema_preview(self):
        """Get schema preview"""
        schema_div = self.driver.find_element(By.ID, "schema-preview")
        return schema_div.text
    
    def get_deployment_status(self):
        """Get deployment status"""
        status_div = self.driver.find_element(By.ID, "deployment-status")
        return status_div.text
    
    def close(self):
        """Close browser"""
        self.driver.quit()
