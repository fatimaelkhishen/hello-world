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
def get_job_links():
    job_links = []
    driver = webdriver.Chrome()
    url = "https://jobs.workable.com/search?location=usa"
    driver.get(url)
    time.sleep(1)
    
    # Dismiss cookie consent dialog if it exists
    try:
        cookie_consent = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-ui='cookie-consent']"))
        )
        cookie_consent.find_element(By.XPATH, "//button[contains(text(), 'Accept')]").click()
    except TimeoutException:
        pass  # Cookie consent dialog not found or already accepted
    
    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobsList__list-item--3HLIF"))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            jobposting = soup.find_all("li", class_="jobsList__list-item--3HLIF")
            for job in jobposting:
                job_links.append("https://jobs.workable.com" + job.find('a')['href'])

            load_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-ui='load-more-button']"))
            )  
            time.sleep(1)
            load_button.click()
        except TimeoutException:
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
        title = soup.find("h1",class_="styles__h2--p4pBC jobOverview__job-title--kuTAQ styles__primary--QTMDv").text
        title = title.strip()
    except:
        title = 'NA'
    try:
        location_element = soup.find("span", class_="jobOverview__job-details--3JOit jobDetails__container--15UJA")
    
        location = location_element.find("span", class_="styles__body--2TdGW jobDetails__job-detail--3As6F styles__primary--QTMDv").text.strip()
        
    except:
        location = 'NA'
    try:
            json_script = soup.find("script", {"type": "application/ld+json"})
            if json_script:
                job_json = json.loads(json_script.string)
                datePosted = job_json.get("datePosted").split("T")[0]
    except:
        datePosted = 'NA'
    try:
        company_text = soup.find("h2", class_="styles__body--2TdGW jobOverview__company--VZQwK companyName__container--cK3_i styles__secondary--f-uLT").text.strip()

        if company_text.lower().startswith("at "):
                    company_text = company_text[3:]
        company = company_text
    except:
        company = 'NA'
    try:
        description = soup.find("div", class_="jobBreakdown__job-breakdown--31MGR").text
    except:
        description = 'NA'

    jobPosting = {
        'SRC_Company': company,
        'Link': job_link,
        'Posting_Date' : datePosted,
        'SRC_Title': title,
        'SRC_Description': description,
        'SRC_Country': location,
        'website': "Workable"
    }
    return jobPosting


def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Workable.xlsx", index=False)

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