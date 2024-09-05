from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC   
from selenium.common.exceptions import NoSuchElementException, TimeoutException  
from selenium import webdriver  
import time  
import random  
import pandas as pd  

def get_job_links():  
    job_links = []   
    driver = webdriver.Chrome()
    base_url = "https://jobs.ajg.com"
    p = 1
    searching = True

    try:  
        while searching:
            # Construct the URL for the current page
            url = f"{base_url}/ajg-home/jobs?page={p}"
            driver.get(url)
            time.sleep(5)  # Allow time for page to load

            # Accept cookies if the button is present
            try:  
                cookie_consent_button = driver.find_element(By.XPATH, '//*[@id="CookieReportsBanner"]/div[1]/div[2]/a[1]')  
                cookie_consent_button.click()  
            except NoSuchElementException:  
                print("Cookie consent button not found, continuing...")  

            try:  
                WebDriverWait(driver, 60).until(  # Increased wait time to 60 seconds  
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-expansion-panel"))  
                )  
            except TimeoutException:  
                print("Timeout waiting for elements to load.")
                break 

            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all(class_="mat-expansion-panel")  
     
            if not listings: 
                print("No listings found on page", p)
                break  

            for listing in listings:  
                job_link_tag = listing.find('a')   
                if job_link_tag and 'href' in job_link_tag.attrs:  
                    job_link = base_url + job_link_tag['href']  
                    job_links.append(job_link)  
             
            # Increment the page number for the next iteration
            p += 1

    finally:
        driver.quit()  # Ensure the driver is closed properly

    return job_links
def construct_job(driver, job_link):   
    driver.get(job_link)  
    time.sleep(5)   
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listings = soup.find_all(class_="mat-expansion-panel")    

    try:  
        title = soup.find('span', {'itemprop': 'title'}).text.strip() 
    except:
        title = "NA"
    try:
        location = soup.find('span',class_="label-value location").text.strip()  
    except:
        location = "NA"
    try:
        job_category = soup.find('span', class_='categories label-value').text.strip()  
    except:
        job_category = "NA"
    try:
        job_type = soup.find('li', id="header-tags3").text.strip()
    except:
        job_type = "NA"
    try:
        desc = soup.find('article', id='description-body').text.strip() 
    except:
        desc = "NA"

        jobPosting = {  
            'SRC_Title': title,  
            'SRC_Country': location,  
            'SRC_Category': job_category,  
            'SRC_Type': job_type,  
            'Website': 'Gallagher',  
            'SRC_Description': desc  
        }  
        return jobPosting  

def save_to_excel(job_data):  
    df = pd.DataFrame(job_data)  
    df.to_excel("Gallagher.xlsx", index=False)  

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