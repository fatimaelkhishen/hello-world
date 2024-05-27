import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def get_job_links():
    job_links = []
    p = 1

    driver = webdriver.Chrome()
    while True:
        url = f"https://www.snagajob.com/search?w=america&radius=20&page={p}"
        
        driver.get(url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("job-card")
        for job_card in job_cards:
            link = job_card.find('meta', itemprop='url').get('content')
            job_links.append(link)
        next_button = soup.find('button', {'aria-label': 'Next page'})
        if not next_button:
            break  # Exit the loop if "Next page" button is not found
        p += 1
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    time.sleep(1)
    try:
        read_more_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Read more job description']")
        read_more_button.click()
    except:
        pass  # Handle the case where the "Read more" button is not found
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find('h1', class_='heading-job-title').text.strip()
    except:
        title = "NA"
    try:
        company = soup.find('a', {'data-snagtag': 'company-name'}).text.strip()
    except:
        company = "NA"
    try:
        estimated_pay = soup.find('td', {'data-snagtag': 'job-est-wage'}).text.strip()
    except:
        estimated_pay = "NA"
    try:
        hours = soup.find('td', {'data-snagtag': 'job-categories'}).text.strip()
    except:
        hours = "NA"
    try:
        location = soup.find('td', {'data-snagtag': 'location'}).text.strip()
    except:
        location = "NA"
    try:
        job_description = soup.find('div', {'data-snagtag': 'job-description'}).text.strip()
    except:
        job_description = "NA"
    try:
        posting_details = soup.find('div', class_='posting-details').text.strip()
        posting_date = posting_details.split('Posted: ')[1].split(' ')[0]
    except:
        posting_date = "NA"

    jobPosting = {
        'SRC_Title': title,
        'SRC_Company': company,
        'SRC_Salary': estimated_pay,
        'SRC_Modality': hours,
        'SRC_Country': location,
        'SRC_Description': job_description,
        'Posting_date': posting_date,
        'Job_Link': job_link,
        'Website': 'Snagajob'
    }
    return jobPosting

def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("jobs.xlsx", index=False)

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