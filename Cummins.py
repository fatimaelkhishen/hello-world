from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd

def get_job_links():
    job_links = set()
    driver = webdriver.Chrome()

    try:
        url = "https://cummins.jobs/usa/jobs/"
        driver.get(url)
        
        # Dismiss cookie banner if present
        try:
            cookie_banner = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cookie-consent__container")))
            cookie_banner.find_element_by_css_selector("button").click()
        except:
            pass
        
        while True:
            try:
                # Click the "More" button
                driver.execute_script("document.getElementById('button_moreJobs').click();")
                
                # Wait for the additional jobs to load
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, "direct_moreLessLinks_listingDiv")))
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, "direct_joblisting")))
                
                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_cards = soup.find_all("li", class_="direct_joblisting")
                for job_card in job_cards:
                    link = job_card.find('a').get('href')
                    job_links.add("https://cummins.jobs" + link)
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                break
            
            # Check if the "More" button is still present, if not, break the loop
            more_button = driver.find_element(By.ID, "button_moreJobs")
            if "display: none;" in more_button.get_attribute("style"):
                break
        
    finally:
        driver.quit()
    
    return job_links



def construct_job(driver, job_link):
    driver.get(job_link)
    # WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, "direct_moreLessLinks_listingDiv")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find('span', itemprop='title').text.strip()
    except:
        title = "NA"
    try:
        location = soup.find('span', itemprop='addressLocality').text.strip()
    except:
        location = "NA"
    try:
        description = soup.find('div', id='direct_jobDescriptionText').text.strip()
    except:
        description = "NA"
    try:
        posting_details = soup.find('meta', itemprop='datePosted')
        posting_date = posting_details['content'][:10]
    except:
        posting_date = "NA"
  
    jobPosting = {
        'SRC_Title': title,
        'SRC_Country': location,
        'SRC_Description': description,
        'Posting_date': posting_date,
        'Job_Link': job_link,
        'Website': 'cummins',
    }
    return jobPosting

def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("cummins    .xlsx", index=False)

def main():
    job_links = get_job_links()
    driver = webdriver.Chrome()
    job_data = []
    for link in job_links:
        job_posting = construct_job(driver, link)
        job_data.append(job_posting)
    driver.quit()
    save_to_excel(job_data)

if __name__ == "__main__":
    main()