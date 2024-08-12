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
import pandas as pd  
from bs4 import BeautifulSoup  
from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
import time  
import random  

def get_job_links(driver):  
    job_links = []  
    p = 1  

    try:  
        while True:  
            url = f"https://www.totaljobs.com/jobs/in-united-states?page={p}"  
            driver.get(url)  
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "res-1p8f8en")))  
            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            job_cards = soup.find_all("article", class_="res-1p8f8en")  
            if not job_cards:  
                break  

            for job_card in job_cards:  
                title = job_card.find("h2", class_="res-1tassqi")  
                if title:  
                    link = title.find('a').get('href')  
                    job_links.append("https://www.totaljobs.com" + link)  

            # Navigate to the next page  
            next_button = soup.find("button", {"aria-label": "Next"})  
            if next_button and "disabled" in next_button.attrs:  
                break  

            p += 1   
            time.sleep(random.uniform(2, 5))  # Randomized sleep time  
    except Exception as e:  
        print(f"An error occurred while getting job links: {e}")  
    return job_links  

def construct_job(driver, job_link):  
    try:  
        driver.get(job_link)  
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'job-ad-display-gro348')))  
        soup = BeautifulSoup(driver.page_source, 'html.parser')
  
        title = soup.find('span', class_='job-ad-display-29uigd').text.strip() if soup.find('span', class_='job-ad-display-29uigd') else "NA"
        company = (soup.find('li', class_='at-listing__list-icons_company-name job-ad-display-62o8fr').text.strip() if soup.find('li', class_='at-listing__list-icons_company-name job-ad-display-62o8fr') else "NA")  
        location = (soup.find('li', class_='at-listing__list-icons_location map-trigger job-ad-display-62o8fr').text.strip() if soup.find('li', class_='at-listing__list-icons_location map-trigger job-ad-display-62o8fr') else "NA")  
        dateposted = (soup.find('li', class_='at-listing__list-icons_date job-ad-display-62o8fr').text.strip() if soup.find('li', class_='at-listing__list-icons_date job-ad-display-62o8fr') else "NA")  
        salary = (soup.find("li", class_="at-listing__list-icons_salary job-ad-display-1dus89x").text.strip() if soup.find("li", class_="at-listing__list-icons_salary job-ad-display-1dus89x") else "NA")  
        job_type = (soup.find("li", class_="at-listing__list-icons_work-type job-ad-display-62o8fr").text.strip() if soup.find("li", class_="at-listing__list-icons_work-type job-ad-display-62o8fr") else "NA")  
        desc = (soup.find('div', class_='at-section-text-jobDescription-content listingContentBrandingColor job-ad-display-1b1is8w').text.strip() if soup.find('div', class_='at-section-text-jobDescription-content listingContentBrandingColor job-ad-display-1b1is8w') else "NA")  

        return {  
            'SRC_Title': title,  
            'SRC_Company': company,  
            'SRC_Country': location,  
            'Posting_date': dateposted,  
            'SRC_Salary': salary,  
            'SRC_Type': job_type,  
            'Job_Link': job_link,  
            'SRC_Description': desc,  
            'Website': 'Totaljobs'  
        }  
    except Exception as e:  
        print(f"Error while fetching job details from {job_link}: {e}")  
        return None  

def save_to_excel(job_data):  
    df = pd.DataFrame(job_data)  
    df.to_excel("Totaljobs.xlsx", index=False)  

def main():  
    driver = webdriver.Chrome()  
    job_links = get_job_links(driver)  
    job_data = []  
    failed_links = []  

    for link in job_links:  
        job_posting = construct_job(driver, link)  
        if job_posting:  
            job_data.append(job_posting)  
        else:  
            failed_links.append(link)  

    driver.quit()  
    save_to_excel(job_data)  

    if failed_links:  
        print(f"Failed to fetch details for the following links: {failed_links}")  

if __name__ == "__main__":  
    main()