import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time
import json
import re
def get_job_links():
    job_links = []
    driver = webdriver.Chrome()
    url = "https://jobs.siemens.com/careers?location=USA"
    driver.get(url)
    time.sleep(1)
    
    # Dismiss cookie consent dialog if it exists
    try:
        cookie_consent = WebDriverWait(driver, 5).until(
             EC.presence_of_element_located((By.XPATH, "//div[@id='uc-show-more']"))
        )
        cookie_consent.find_element(By.XPATH, "//button[contains(text(), 'Accept')]").click()
    except TimeoutException:
        pass  # Cookie consent dialog not found or already accepted
    
    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-card-container list  "))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            jobposting = soup.find_all("div", class_="job-card-container list  ")
            for job in jobposting:
                job_links.append("https://jobs.siemens.com" + job.find('a')['href'])

            # Try to find the "Load More" button  
            load_button = WebDriverWait(driver, 10).until(  
                EC.element_to_be_clickable((By.XPATH, "//*[@id='pcs-body-container']/div[2]/div[2]/div/div[1]/div/div[11]/button"))  
            )  

            # Click the "Load More" button  
            load_button.click()  
            time.sleep(2)  # Give some time for the new job cards to load  
        except (TimeoutException, NoSuchElementException):  
            # No more jobs to load, break the loop  
            print("No more job postings to load.")  
            break  
        except Exception as e:  
            print("An error occurred:", e)  
            break 
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find("h3",class_="job-card-title").text
        title = title.strip()
    except:
        title = 'NA'
    try:
        location_element = soup.find("p", class_="position-location")
    
        location = location_element.find("span", class_="position-location").text.strip()
        
    except:
        location = 'NA'
    # Find all job containers
    job_containers = soup.find_all("div", class_="job-card-container list")

    for job in job_containers:
        try:
            job_id = job.find_all("div", class_="custom-jd-field col-md-2")[0].text.strip()
        except:
            job_id = "NA"
        try: 
            company = job.find_all("div", class_="custom-jd-field col-md-2")[1].text.strip()
        except:
            company = "NA"
        try:
            organization = job.find_all("div",class_="custom-jd-field col-md-2")[2].text.strip()
        except:
            organization = "NA"
        try:
            job_family = job.find_all("div",class_="custom-jd-field col-md-2")[3].text.strip()
        except:
            job_family = "NA"
        try:
            experience_level = job.find_all("div", class_="custom-jd-field col-md-2")[4].text.strip()
        except:
            experience_level = "NA"
        try:
            job_type = job.find_all("div", class_="custom-jd-field col-md-2")[5].text.strip()
        except:
            job_type = "NA"
    try:
        description = soup.find("div", class_="col-md-12").text
    except:
        description = 'NA'

    jobPosting = {
        'SRC_Company': company,
        'Link': job_link,
        'SRC_Title': title,
        'JOB_ID':job_id,
        'SRC_ORGANIZATION': organization,
        'JOB_FAMILY':job_family,
        'SRC_EXPERIENCE':experience_level,
        'job_type': job_type,
        'SRC_Description': description,
        'SRC_Country': location,
        'website': "Siemens"
    }
    return jobPosting


def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Siemen.xlsx", index=False)

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