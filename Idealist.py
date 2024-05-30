import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_job_links():
    job_links = []
    driver = webdriver.Chrome()
    page = 1
    searching = True
    while searching:
        url = f"https://www.idealist.org/en/jobs?page={page}&q=usa"
        driver.get(url)
        time.sleep(2)
        job_elements = driver.find_elements(By.XPATH, "//div[@data-qa-id='search-result']")
        if not job_elements:
            searching = False
            continue
        jobs = [ a.get_attribute('href')
         for job_element in job_elements for a in job_element.find_elements(By.XPATH, ".//a[@data-qa-id='search-result-link']")]
        if not jobs:
            searching = False
            continue
        job_links.extend(jobs)
        page += 1
    return job_links
def listInfoToDict(UL):
    out = {}
    for each in UL:
        key = each.find_element(By.XPATH,
                                    ".//h5").text.lower().strip().replace(" ", "_")
        value = each.find_element(By.XPATH, ".//div/span").text
        out[key] = value
    return out
def getOptionalInfo(divs):
    out = {}
    divs = divs[1:-1]
    for div in divs:
        try:
            key = div.find_element(By.XPATH,
                                    ".//h3").text.lower().strip().replace(" ", "_")
            if key == "location":
                value = div.find_element(By.XPATH,
                                            ".//div/div").text.lower()
            elif key == "salary":
                value = div.find_element(By.XPATH, ".//span").text
            elif key == "details_at_a_glance":
                continue
            else:
                readmore = div.find_element(By.XPATH,".//a")
                readmore.click()
                value = div.find_element(By.XPATH, "./div").text.replace("Read less about benefits",".")
            out[key] = value
        except:
            pass 
    return out



def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        jobTitleElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@data-qa-id='listing-name']"))
        )
        jobTitle = jobTitleElement.text.split('-')[0].strip()
    except:
        jobTitle = "NA"
    try:
        companyNameElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-qa-id='org-link']"))
        )
        companyName = companyNameElement.text
    except:
        companyName = "NA"

    # Extract date from the JSON-LD script
    try:
        json_script = soup.find("script", {"type": "application/ld+json"})
        if json_script:
            job_json = json.loads(json_script.string)
            date = job_json.get("datePosted").split("T")[0]
        else:
            date = "NA"
    except:
        date = "NA"

    try:
        readMore = driver.find_element(By.XPATH,
                                                '/html/body/div/div/div[3]/div[1]/div/div[2]/div/div[3]/div/div/a')
        readMore.click()
        jobDescription = driver.find_element(By.XPATH,
                                                    '/html/body/div/div/div[3]/div[1]/div/div[2]/div/div[1]/div/div').text
    except:
        jobDescription = "NA"

    detailsUL = driver.find_elements(By.XPATH,
                                            "/html/body/div[1]/div/div[1]/div[6]/div/div/div[3]/div[2]/ul/li")
    details = listInfoToDict(detailsUL)
    divs = driver.find_elements(By.XPATH,
                                        "/html/body/div[1]/div/div[1]/div[6]/div/div/div[3]/div")
    tabs = getOptionalInfo(divs)
    jobPosting = {
        "SRC_Company": companyName,
        "SRC_Title": jobTitle,
        "SRC_Description": jobDescription,
        "SRC_Country": "USA",
        "Posting_Date": date,
        "Link": job_link,
        "Webiste": "Idealist"
    }
    jobPosting.update(details)
    jobPosting.update(tabs)
    return jobPosting


def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Idealist.xlsx", index=False)

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