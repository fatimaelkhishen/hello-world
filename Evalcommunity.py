import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_job_links():
    job_links = []
    driver = webdriver.Chrome()
    driver.get("https://www.evalcommunity.com/find-jobs/?search_location=USA")
    time.sleep(2)  
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".job_listings"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.find_all("li", class_="job_listing")
   

        for listing in listings:
            job_link = listing.find("a")['href']
            job_links.append(job_link)
    except :
        print(f"Timed out waiting")

    return job_links


def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        title = soup.find('h1').text.strip()
    except:
        title = "NA"

    try:
        description = soup.find("div", class_="job-description").text.strip()
    except:
        description = "NA"

    try:
        company_info = soup.find("div", class_="job-company-info")
        company_name = company_info.find("h3").text.strip()   
    except:
        company_name = "NA"

    try:
        location = soup.find("div", class_="single-job-overview-location").find("a").text.strip()
    except:
        location = "NA"
    try:
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        script_content = script_tag.string.strip()
        match = re.search(r'"dateModified"\s*:\s*"([^"]+)"', script_content)
        if match:
            Date = match.group(1)
            postingdate = Date.split('T')[0]
    except:
        postingdate = "NA"

    try:
        valid_through = soup.find("div", class_="single-job-overview-expiration-date").find("span").text.strip()
    except:
        valid_through = "NA"

    jobposting = {
        "SRC_Title": title,
        "SRC_Description": description,
        "SRC_Country": location,
        "Posting_Date": postingdate,
        "Expiration_Date": valid_through,
        "SRC_Company": company_name,
        "Link": job_link,
        "Website":"Evalcommunity"
    }

    return jobposting

def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Evalcommunity.xlsx", index=False)

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