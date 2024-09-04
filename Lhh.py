import pandas as pd  
from bs4 import BeautifulSoup  
from selenium import webdriver  
import time  
import random  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  

def get_job_links():  
    job_links = []  
    driver = webdriver.Chrome()  
    driver.get("https://www.lhh.com/us/en/search-jobs/?s=date&pg=1&t=&loc=United+States&rid=E8B32C77-F7A9-4344-8EC4-2C7CF5315ED6&range=25")  
    time.sleep(5)  
    base_url = "https://www.lhh.com"  
    page_number = 1  

    try:  
         
        try:  
            cookie_consent_button = WebDriverWait(driver, 10).until(  
                EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))  
            )  
            cookie_consent_button.click()  
            print("Clicked on cookie consent button.")  
        except Exception as e:  
            print(f"Cookie consent button not found or already accepted: {e}")  

        while True:  
            try:  
                 
                WebDriverWait(driver, 30).until(  
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".c-job-listing-card"))  
                )  
            except Exception as e:  
                print(f"Timeout while waiting for job listings: {e}")  
                break  
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all("li", class_="c-job-listing-card")  

            if not listings:  
                print("No listings found. Exiting...")  
                break  

              
            for listing in listings:  
                try:  
                    job_link = listing.find("a")['href']  
                    if job_link:  
                        if job_link.startswith('/'):  
                            job_link = base_url + job_link  
                        job_links.append((job_link, page_number))    
                except Exception as e:  
                    print(f"Error retrieving job link: {e}")   

            try:  
                 
                next_button = WebDriverWait(driver, 10).until(  
                    EC.element_to_be_clickable((By.XPATH, "//a[@class='c-job-listing-left__right-arrow' and @data-next]"))  
                )  
                
                  
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)  
                
                 
                driver.execute_script("arguments[0].click();", next_button)  
                time.sleep(random.uniform(2, 5))   
                page_number += 1  
            except Exception as e:  
                print(f"Exception occurred while navigating to the next page: {e}")  
                break  

    finally:  
        driver.quit()  

    return job_links  

def construct_job(driver, job_link):  
    driver.get(job_link)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')  

    try:  
        jobTitle = soup.find("p", class_="c-job-listing-card__header").text.strip()  
    except Exception:  
        jobTitle = "NA"        

      
    try:  
        Salary = soup.find_all("div", class_="c-job-details-mobile__information")[0].find("p", class_="c-job-details__category").text.strip()  
    except Exception:  
        Salary = "NA"   

    
    try:  
        Job_type = soup.find_all("div", class_="c-job-details-mobile__information")[1].find("p", class_="c-job-details__category").text.strip()  
    except Exception:  
        Job_type = "NA"  
 

      
    try:  
        Location = soup.find_all("div", class_="c-job-details-mobile__information")[2].find("p", class_="c-job-details__category").text.strip()  
    except Exception:  
        Location = "NA"   

    try:   
        companyName = soup.find("div", class_="employer-date-container").find_all("p")[0].text.strip()    
    except Exception:  
        companyName = "NA"  

    try:  
        Date_posted = soup.find("div", class_="employer-date-container").find_all("p")[1].text.strip()    
    except Exception:  
        Date_posted = "NA"  

     
    try:  
        jobDescription = soup.find("section", class_="c-job-details-mobile__description").text.strip() 
    except Exception:  
        jobDescription = "NA"

    jobPosting = {  
        "SRC_Title": jobTitle,  
        "SRC_Company": companyName,   
        "SRC_Description": jobDescription,  
        "SRC_Country": Location,    
        "Date_posted": Date_posted,  
        "SRC_Salary": Salary,  
        "SRC_Type": Job_type,  
        "Link": job_link,  
        "Website": "LHH"  
    }  

    return jobPosting  

def save_to_excel(job_data):  
    df = pd.DataFrame(job_data)  
    df.to_excel("LHH.xlsx", index=False)  

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