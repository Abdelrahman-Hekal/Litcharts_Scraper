from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import pandas as pd
import time
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def set_driver_options():

    # Setting up chrome driver for the bot
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.page_load_strategy = 'normal'

    return chrome_options

def initialize_bot():

    # Setting up chrome driver for the bot
    chrome_options = set_driver_options()

    try:
        driver = uc.Chrome(options=chrome_options) 
    except:
        # Setting up chrome driver for the bot
        options = set_driver_options()
        # installing the chrome driver
        chrome_service = ChromeService()
        # configuring the driver
        driver = webdriver.Chrome(options=options, service=chrome_service)
        ver = int(driver.capabilities['chrome']['chromedriverVersion'].split('.')[0])
        driver.quit()

        undetected = False
        try:
            driver = uc.Chrome(version_main = ver, options=chrome_options) 
            undetected = True
        except:
            try:
                print('Failed to locate the Chrome driver online, searching for the driver locally in: C:\Chromedriver')
                chrome_options = set_driver_options()
                chrome_options.add_argument('--disable-dev-shm-usage') 
                driver = uc.Chrome(driver_executable_path="C:\\Chromedriver\\chromedriver.exe", options=chrome_options) 
                undetected = True
            except Exception as err:
                pass

        if not undetected:
            print('Failed to initialize undetected-chromedriver, using the basic driver version instead')
            chrome_options = set_driver_options()
            driver = webdriver.Chrome(options=chrome_options, service=chrome_service) 

    driver.set_window_size(1920, 1080)
    driver.maximize_window()
    driver.set_page_load_timeout(120)

    return driver

def scrape_litcharts():
        
    start = time.time()
    print('-'*75)
    print('Scraping Litcharts.com ...')
    
    # initialize the web driver
    driver = initialize_bot()
    # initializing the output dataframe
    df = pd.DataFrame()
    links = ['https://www.litcharts.com/lit', 'https://www.litcharts.com/poetry']
    for link in links:
        driver.get(link)
        print('-'*75)
        print(f'Scraping data from: {link}')
        print('Loading all the titles ...')

        while True:
            # scrolling across the page 
            try:
                total_height = driver.execute_script("return document.body.scrollHeight")
                height = total_height/10
                new_height = 0
                for _ in range(10):
                    prev_hight = new_height
                    new_height += height             
                    driver.execute_script(f"window.scrollTo({prev_hight}, {new_height})")
                    time.sleep(0.1)
            except:
                pass

            try:
                button = wait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='btn btn-lg btn-default']")))
                driver.execute_script("arguments[0].click();", button)
                time.sleep(5)
            except:
                break

        results = wait(driver, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[class='guide-list__guide']")))
        n = len(results)

        for i, res in enumerate(results):
            
            row = {}

            #title
            title = ''
            try:
                title = wait(res, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='title-5']"))).get_attribute('textContent').strip()
            except:
                pass

            row['Title'] = title

            #author
            author = ''
            try:
                author = wait(res, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='body-2']"))).get_attribute('textContent').strip()
            except:
                pass

            row['Author'] = author

            #genre
            genre = ''
            try:
                genre = wait(res, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='guide-list__guide--type subtitle-2']"))).get_attribute('textContent').strip()
            except:
                pass

            row['Genre'] = genre

            row['Title Link'] = res.get_attribute('href')

            df = pd.concat([df, pd.DataFrame([row.copy()])], ignore_index=True)
            print(f'title {i+1}/{n} is scraped successfully')
            # saving data to csv file each 100 links
            if np.mod(i+1, 100) == 0:
                print('Outputting scraped data ...')
                df.to_excel('Litcharts_Data.xlsx', index=False)

    df.to_excel('Litcharts_Data.xlsx', index=False)
    elapsed = round((time.time() - start)/60, 2)
    print('-'*75)
    print(f'Litcharts.com scraping process completed successfully! Elapsed time {elapsed} mins')
    print('-'*75)
    driver.quit()

if __name__ == "__main__":

    scrape_litcharts()