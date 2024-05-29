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
        url = f"https://www.totaljobs.com/jobs/in-united-states?page={p}"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("article", class_="res-vxbpca")
        for job_card in job_cards:
            title = job_card.find("h2", class_="res-1tassqi")
            link = title.find('a').get('href')
            job_links.append("https://www.totaljobs.com"+link)
        next_button = soup.find("button", {"aria-label": "Next"})
        if next_button and "disabled" in next_button.attrs:
            break
    
        p += 1
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find('span', class_='job-ad-display-1amara9').text.strip()
    except:
        title = "NA"
    try:
        company = soup.find('li', class_='at-listing__list-icons_company-name job-ad-display-iwio6d').text.strip()
    except:
        company = "NA"
    try:
        location = soup.find('li', class_='at-listing__list-icons_location map-trigger job-ad-display-iwio6d').text.strip()
    except:
        location = "NA"
    try:
            script_tag = soup.find('script', type='application/ld+json')

            if script_tag:
                script_content = script_tag.string
                match = re.search(r'"datePosted":\s*"([^"]+)"', script_content)
                if match:
                    dateposted = match.group(1).split('T')[0]
    except:
        dateposted = "NA"
    try:
        Salary = soup.find("li", class_="at-listing__list-icons_salary job-ad-display-1q4rjik").text.strip()
    except:
        Salary = "NA"
    try:
        type = soup.find("li", class_="at-listing__list-icons_work-type job-ad-display-iwio6d").text.strip()
    except:
        type = "NA"
    try:
        desc = soup.find('span', class_='job-ad-display-bjugyt').text.strip()
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
        'Website': 'Totaljobs'
    }
    return jobPosting


def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Totaljobs.xlsx", index=False)

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