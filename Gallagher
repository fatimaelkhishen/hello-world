from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC   
from selenium.common.exceptions import NoSuchElementException, TimeoutException  
from selenium import webdriver  
import time  
import random  
import pandas as pd  

def get_job_links(driver):  
    job_links = []   
    driver.get("https://jobs.ajg.com/ajg-home/jobs")  
    time.sleep(5)  
    base_url = "https://jobs.ajg.com"  

    try:  
        try:  
            cookie_consent_button = driver.find_element(By.XPATH, '//*[@id="CookieReportsBanner"]/div[1]/div[2]/a[1]')  
            cookie_consent_button.click()  
        except NoSuchElementException:  
            print("Cookie consent button not found, continuing...")  

        while True:  
            # Adjust the wait time if needed  
            try:  
                WebDriverWait(driver, 60).until(  # Increased wait time to 60 seconds  
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-expansion-panel"))  
                )  
            except TimeoutException:  
                print("Timed out waiting for the element to be present.")  
                break  # Exit the loop if we can't find the panel  

            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all(class_="mat-expansion-panel")  

            # Check if we found any listings on this page  
            if not listings:  
                print("No job listings found on this page.")  
                break  # Exit if no listings are found  

            for listing in listings:  
                job_link_tag = listing.find('a')   
                if job_link_tag and 'href' in job_link_tag.attrs:  
                    job_link = base_url + job_link_tag['href']  
                    job_links.append(job_link)  

            # Print the job links found on the current page  
            print(f"Found {len(listings)} job links on this page: {job_links[-len(listings):]}")  # Print the newly found links  

            try:   
                next_button = WebDriverWait(driver, 10).until(  
                    EC.visibility_of_element_located((By.XPATH, '//button[@aria-label="Next Page of Job Search Results"]'))  
                )  

                # Check if next button is enabled or not  
                if next_button.is_displayed() and "disabled" not in next_button.get_attribute("class"):    
                    driver.execute_script("arguments[0].scrollIntoView();", next_button)  
                    driver.execute_script("arguments[0].click();", next_button)  
                    time.sleep(random.uniform(2, 5))   
                else:    
                    print("No more pages to navigate.")  
                    break  
            except Exception as e:  
                print(f"Exception occurred while navigating pages: {e}")  
                break   

    finally:  
        driver.quit()    
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
    driver = webdriver.Chrome()  
    job_links = get_job_links(driver)  
    job_data = []  
    for link in job_links:  
        job_posting = construct_job(driver, link)  
        if job_posting:  
            job_data.append(job_posting)  
    driver.quit()  
    save_to_excel(job_data)  

if __name__ == "__main__":  
    main()