import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re


def get_job_links():
    job_links = []
    p = 1

    driver = webdriver.Chrome()
    while True:
        url = f"https://www.reed.co.uk/jobs/jobs-in-usa?sortBy=displayDate&pageno={p}"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("article", class_="card job-card_jobCard__MkcJD")
        for job_card in job_cards:
            link = job_card.find('a').get('href')
            job_links.append("https://www.reed.co.uk"+link)
        next_button = soup.find("li", class_="page-item disabled")
        if not next_button:
            break
    
        p += 1
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find('h1').text.strip()
    except:
        title = "NA"
    try:
        posted_div = soup.find('div', class_='posted')

        # Extract the company name
        if posted_div:
            company_span = posted_div.find('span', itemprop='name')
            if company_span:
                company = company_span.get_text(strip=True)
    except:
        company = "NA"
    try:
        location = soup.find('span', itemprop='addressLocality').text.strip()
    except:
        location = "NA"
    try:
        posted_div = soup.find('div', class_='posted')

        # Extract the date from the <meta> tag
        if posted_div:
            date_meta_tag = posted_div.find('meta', itemprop='datePosted')
            if date_meta_tag:
                dateposted = date_meta_tag['content']
    except:
        dateposted = "NA"
    try:
        Salary = soup.find('span', itemprop='baseSalary').find('span').text.strip()
    except:
        Salary = "NA"
    try:
        type = soup.find('span', itemprop='employmentType').text.strip()
    except:
        type = "NA"
    try:
        desc =soup.find('span', itemprop='description').text.strip()
    except:
        desc = "NA"

    jobPosting = {
        'SRC_Title': title,
        'SRC_Company': company,
        'SRC_Country': location,
        'Posting_date': dateposted,
        'SRC_Salary': Salary,
        'SRC_Type':type,
        'Job_Link': job_link,
        'SRC_Description': desc,
        'Website': 'Reed'
    }
    return jobPosting


def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Reed.xlsx", index=False)

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