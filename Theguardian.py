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
from json import JSONDecoder
import re


def extract_json_objects(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data
    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.
    """
    pos = 0
    while True: 
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1
def get_job_links():
    job_links = []
    searching = True
    page = 1
    driver = webdriver.Chrome()
    
    # Dismiss cookie consent dialog if it exists
    try:
        cookie_consent = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-ui='cookie-consent']"))
        )
        cookie_consent.find_element(By.XPATH, "//button[contains(text(), 'Accept')]").click()
    except TimeoutException:
        pass  # Cookie consent dialog not found or already accepted
    
    while searching:
        driver.get("https://jobs.theguardian.com/jobs/north-america/" + str(page))
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        except:
            searching = False
        urlBase = "https://jobs.theguardian.com"
        jobs = [urlBase + x.find("a")["href"].strip()
                for x in soup.find_all("h3", class_="lister__header")]
        if len(jobs) == 0:
            break
        
        job_links.extend(jobs)
        
        next_button = soup.find("span", class_="disabled")
        if next_button and "Next" in next_button.get_text():
            searching = False
        
        page += 1
        
    driver.quit()
    return job_links


def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        jobTitle = soup.find("h1", class_="mds-font-s6").text
    except:
        jobTitle = "NA"
    try:
        job_description = soup.find(id="job-description").text
    except:
        try:
            job_description = soup.find(
                class_="mds-edited-text mds-font-body-copy-bulk").text
        except:
            job_description = "NA"
    try:
        Company_name = soup.find("dt", string="Employer").find_next("dd").text.strip()
    except:
        Company_name = "NA"
    try:
        location = soup.find("dt", string="Location").find_next("dd").text.strip()
    except:
        location = "NA"
    try:
        salary = soup.find("dt", string="Salary").find_next("dd").text.strip()
    except:
        salary = "NA"
    job_expired = False
    expired_alert = soup.find("div", role="alert")
    if expired_alert and "This job has expired" in expired_alert.text:
        job_expired = True
        # Attempt to extract the posted date from the ClientGoogleTagManagerDataLayer script
        for script in soup.find_all("script"):
            if 'ClientGoogleTagManagerDataLayer' in script.text:
                data_layer = next(extract_json_objects(script.text), None)
                if data_layer and "JobDatePosted" in data_layer:
                    posted_date = data_layer["JobDatePosted"]
                    break
        else:
            posted_date = "NA"
    else:
        try:
            script_element = soup.find('script', type='application/ld+json')
            json_data = json.loads(script_element.contents[0])
            Date_of_Posting = json_data.get('datePosted', None)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', Date_of_Posting)
            posted_date = date_match.group(1) if date_match else "NA"
        except:
            # If the above fails, fallback to attempting to extract the "Closing date"
            posted_date = "NA"  # Default to "NA" if both methods fail
    try:
        Industry = soup.find("dt", string="Industry").find_next("dd").text.strip().replace('\n', '')
    except:
        Industry = "NA"
    try:
        Job_level = soup.find("dt", string="Job level").find_next("dd").text.strip()
    except:
        Job_level = "NA"
    try:
        Listing_type = soup.find("dt", string="Listing type").find_next("dd").text.strip()
    except:
        Listing_type = "NA"
    try:
        Education_level = soup.find("dt", string="Education level").find_next("dd").text.strip()
    except:
        Education_level = "NA"
    try:
        hours = soup.find("dt", string="Hours").find_next("dd").text.strip()
    except:
        hours = "NA"
    try:
        workplace = soup.find("dt", string="Workplace").find_next("dd").text.strip()
    except:
        workplace = "NA"
    try:
        contract = soup.find("dt", string="Contract").find_next("dd").text.strip()
    except:
        contract = "NA"
    
    jobPosting = {
        "SRC_Title": jobTitle,
        "SRC_Description": job_description,
        "Link": job_link,
        'Posting_Date': posted_date,
        'Expired': job_expired,
        'SRC_Country': location,
        'SRC_Industry': Industry,
        'SRC_Company': Company_name,
        'Salary': salary,
        "Job Level": Job_level,
        "Listing Type": Listing_type,
        "Education": Education_level,
        "Hours": hours,
        "Workplace": workplace,
        "Contract": contract,
        "Website":"Theguardian"
    }
    return jobPosting


def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Theguardian.xlsx", index=False)

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