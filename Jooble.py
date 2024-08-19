import pandas as pd  
from bs4 import BeautifulSoup  
from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
import time  

def get_job_links():  
    job_links = []  
    p = 1  # Start from page 1  
    driver = webdriver.Chrome()  

    while True:  
        url = f"https://jooble.org/SearchResult?rgns=united%20states&page={p}"  
        print(f"Accessing page: {url}")  # Debugging output  

        driver.get(url)  
        time.sleep(5)  # Increased wait for page loading   
        
        # Check and dismiss cookie consent if it appears  
        try:  
            consent_button = WebDriverWait(driver, 10).until(  
                EC.element_to_be_clickable((By.XPATH, '//*[@id="cookiescript_accept"]'))  
            )  
            consent_button.click()  
            print("Cookie consent accepted.")  
            time.sleep(1)   
        except Exception as e:  
            print("No cookie consent button found or error occurred:", e)  

        # Check for job cards presence  
        try:  
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ojoFrF")))  
            print("Job cards are present.")  
        except Exception as e:  
            print("Job cards not found after waiting:", e)  
            break  

        # Parse the page with BeautifulSoup  
        soup = BeautifulSoup(driver.page_source, 'html.parser')  
        job_cards = soup.find_all("li", class_="ojoFrF")  # Simplify class name here to see if it matches any actual card  
        
        # Debug: Print page source for verification  
        # print(soup.prettify())  
        
        if not job_cards:  
            print("No job cards found on this page.")  
            break   
        
        for job_card in job_cards:  
            title = job_card.find("h1")  # Might need to adjust this class name as well  
            if title:  
                link = title.find('a').get('href')  
                job_links.append(link)  
                print(f"Job link added: {link}")  
        
        p += 1  # Increment the page number  

    driver.quit()  
    return job_links  

# Example usage  
if __name__ == "__main__":  
    links = get_job_links()  
    print("Job Links:")  
    for link in links:  
        print(link)