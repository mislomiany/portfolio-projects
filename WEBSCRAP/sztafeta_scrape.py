# %%

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import re



def scroll_down(driver):
    web_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == web_height:
            break
        else:
            web_height = new_height
    
    print("Done with scrolling!")
    return None



url = r"https://www.hejto.pl/tag/sztafeta"
chromedriver_path = r"D:\KOD\chromedriver.exe"
options = Options()
options.add_argument("--disable-notifications")
options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])

driver = webdriver.Chrome(chromedriver_path, chrome_options = options)
driver.get(url)

time.sleep(3)
try:
    popup_handler = driver.find_element(By.XPATH, '//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]')
    popup_handler.click()
except:
    print("No privacy")
time.sleep(30)
try:
    zaloz_konto = driver.find_element(By.XPATH, '//*[@id="RegisterDialog"]/div/div/button')
    zaloz_konto.click()
except:
    print("What about the account prompt?")
try:
    patronite = driver.find_element(By.XPATH, '//*[@id="__next"]/div/header/div[2]/button')
    patronite.click()
except:
    print("No more patronite?")


# %%

pattern = re.compile(r"((\d[\d,.\s]+)([\d\s+,.]+)=\s?(\d[\d,. ]+))")

db = pd.DataFrame(columns=["User",
                           "Start",
                           "Dodane",
                           "Koniec",
                           "DodaneSuma",
                           "CRC",
                           "Kontinuum"])
loops = 0
end_flag = True

while loops < 50 and end_flag:
    scroll_down(driver)
    
    soup = BeautifulSoup(driver.page_source, "lxml")
    articles = soup.find_all("div", class_= "flex flex-col gap-4")

    for article in articles[1:]:
        post = article.find("div", class_="relative flex flex-col gap-3")
        # print(post.text)
        user = post.find("span", class_="flex items-center gap-1.5 whitespace-nowrap text-ellipsis text-textPrimary-light dark:text-textPrimary-dark block font-semibold w-full sm:w-auto text-ellipsis max-w-username md:max-w-galleryOneImage overflow-hidden hover:text-primary-main focus:text-primary-main dark:hover:text-primary-main dark:focus:text-primary-main text-sm").text
        print("#####" * 20)
        print(user)
        tekst = post.find("div", class_="relative").text.replace("\xa0","")
        print(tekst)

        if ("#poprawnywyniksztafeta" in tekst):
            finding = re.search(r"[=]?\s?(\d[\d,.]+\b)", tekst)
            poprawka = float(finding.group(1).replace(",","."))
            db = pd.concat([db, 
                            pd.DataFrame({"User": [user],
                                    "Start": [""],
                                    "Dodane": [""],
                                    "Koniec": [poprawka],
                                    "DodaneSuma": [""],
                                    "CRC": [""],
                                    "Kontinuum": [""]})],
                            axis=0, ignore_index=True)
            print("Dodany poprawny wynik!")
            continue

        wpis = re.search(pattern, tekst)

        try:
            start = float(wpis.group(2).replace(",",".").replace(" ",""))
            dodane = wpis.group(3).strip("+ ").replace(",",".")
            koniec = float(wpis.group(4).replace(",",".").replace(" ","").strip("."))
        except:
            print("\nNCan't process data")
            print(f"Regex: {wpis}")
            continue

        try:
            dataframe = pd.DataFrame({"User": [user],
                                        "Start": [start],
                                        "Dodane": [dodane],
                                        "Koniec": [koniec],
                                        "DodaneSuma": [round(float(eval(dodane)),2)],
                                        "CRC": [str(round(koniec-start,2) == round(eval(dodane),2))],
                                        "Kontinuum": [""]})
            db = pd.concat([db, dataframe], axis=0, ignore_index=True)
            print("Dodane!")

            try:
                db.iloc[-1,-1] = str(db.iloc[-2,1] == db.iloc[-1, -4])
            except:
                print("Problem with continuum")
            
        except:
            print("I can't merge")

        # Adding manually the first entry
        if start == 10.02:
            dataframe = pd.DataFrame({"User": ["rakaniszu"],
                                    "Start": [0.00],
                                    "Dodane": ["10.02"],
                                    "Koniec": [10.02],
                                    "DodaneSuma": ["10.02"],
                                    "CRC": ["hardcoded"],
                                    "Kontinuum": ["hardcoded"]})
            db = pd.concat([db, dataframe], axis=0, ignore_index=True)
            end_flag = False

    loops += 1

    try:
        try:
            next_page = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div[1]/div[3]/a[2]')
        except:
            next_page = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div[1]/div[3]/a[1]')

        print("Click!")
        next_page.click()
        time.sleep(3)
    except:
        print("Kurwa")
        break

db.to_csv(r"D:\KOD\database_sztafeta.csv")
print("Koniec")
    # %%
print(driver.document.body.scrollHeight)
# %%
driver.execute_script("return document.documentElement.scrollHeight")
# %%
