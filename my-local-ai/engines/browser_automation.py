from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

class BrowserAutomation:
    """Automate web browsing and data extraction."""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def start_browser(self):
        """Initialize Chrome browser."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-notifications')
            options.add_argument('start-maximized')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            return True
        except Exception as e:
            return False
    
    def close_browser(self):
        """Close browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def navigate(self, url):
        """Navigate to URL."""
        try:
            if not self.driver:
                self.start_browser()
            
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            return True
        except Exception as e:
            return False
    
    def get_page_content(self):
        """Extract page content."""
        try:
            if not self.driver:
                return None
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:2000]  # Limit to 2000 chars
        except Exception as e:
            return None
    
    def search_google(self, query):
        """Search Google for information."""
        try:
            if not self.driver:
                self.start_browser()
            
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self.driver.get(url)
            time.sleep(2)
            
            # Extract search results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            results = []
            
            # Find result links
            for g in soup.find_all('div', class_='g'):
                try:
                    title = g.find('h3')
                    link = g.find('a')
                    
                    if title and link:
                        results.append({
                            "title": title.get_text(),
                            "url": link.get('href'),
                            "snippet": g.find('span', class_='aCOpf').get_text() if g.find('span', class_='aCOpf') else ""
                        })
                except:
                    pass
            
            return results[:5]  # Top 5 results
        except Exception as e:
            return []
    
    def click_element(self, selector):
        """Click an element on page."""
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            time.sleep(1)
            return True
        except Exception as e:
            return False
    
    def fill_form(self, fields):
        """Fill form fields."""
        try:
            for selector, value in fields.items():
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                element.clear()
                element.send_keys(value)
                time.sleep(0.5)
            return True
        except Exception as e:
            return False
    
    def get_links(self):
        """Extract all links from page."""
        try:
            if not self.driver:
                return []
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                if href and text:
                    links.append({"text": text, "url": href})
            
            return links[:10]  # Top 10 links
        except:
            return []
    
    def extract_data_table(self):
        """Extract table data from page."""
        try:
            if not self.driver:
                return []
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            tables = []
            
            for table in soup.find_all('table')[:3]:  # First 3 tables
                rows = []
                for tr in table.find_all('tr')[:10]:  # First 10 rows
                    cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                    if cells:
                        rows.append(cells)
                if rows:
                    tables.append(rows)
            
            return tables
        except:
            return []
