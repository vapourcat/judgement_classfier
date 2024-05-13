import os
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def file_download(elements_title,num,court_number):
    if elements_title is None:
        return False
    else:
        index=0 #每頁20個文本的索引
        sum = 0 # 計算是否已達到500筆
        pattern = r'(?:審|調|補|促|抗|消|更|上|續|救|他|聲|附民)\s字'
        
        while sum<500:
            for title in elements_title:
                matches = re.search(pattern, title.text)
                if matches==None: #判斷字號是否需要剃除
                    href = elements_title[index].get_attribute('href')
                    if href is not None:
                        if num>4988:
                            response = requests.get(href)
                            soup = BeautifulSoup(response.text, 'html.parser')
                            if court_number==0: #判斷是否為憲法法庭
                                # all_text_li = soup.find_all('li', class_='text')
                                # html_content = all_text_li[-2].get_text()
                                all_text_li = soup.find_all('li', title='理由')
                                html_content = all_text_li[-1].get_text()
                            else:
                                html_content = soup.find('div', class_='htmlcontent').get_text()
                                if html_content=="":
                                    html_content = soup.find('div', class_='text-pre text-pre-in').get_text()
                                
                            folder_name = "Welfare"
                            file_name = str(num) + ".txt"
                            file_path = os.path.join(folder_name, file_name)

                            if not os.path.exists(folder_name): #檢查資料夾是否存在
                                os.makedirs(folder_name)
                            with open(file_path, "w", encoding="utf-8") as file:
                                file.write(html_content)
                            print(f"第{num}筆 {title.text} 已成功下載")
                        num+=1
                sum+=1
                index+=1
            try:
                next_page = driver.find_element(By.XPATH, '//*[@id="hlNext"]')
                next_page.click() # 點擊下一頁

                elements_title = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.ID, "hlTitle"))
                )
            except:
                break
            index = 0
        # 切換回主要的HTML頁面
        driver.switch_to.default_content()
        return num
        
def court_switch(court,court_index,num):
    if court==None:
        return False
    else:        
        court.click()
        
        iframe = WebDriverWait(driver, 10).until(   
            EC.presence_of_element_located((By.ID, 'iframe-data'))
        )
        driver.switch_to.frame(iframe)

        elements_title = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, "hlTitle"))
        )

        num = file_download(elements_title,num,court_index)
        
        court_index+=1
        court = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="collapseGrpCourt"]/div/ul/li[' + str(court_index+1) + ']' + '/a'))
        )
        return court_switch(court,court_index,num)

        
driver = webdriver.Chrome(ChromeDriverManager().install())
url = "https://judgment.judicial.gov.tw/FJUD/default.aspx"
driver.get(url)

search = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="txtKW"]'))
)
search.clear()
search.send_keys('兒童及少年福利與權益保障法')
search.send_keys(Keys.RETURN)

court_index=0
court = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="collapseGrpCourt"]/div/ul/li[' + str(court_index+1) + ']' + '/a'))
)

num = 1 #共抓到幾筆資料
        
court_switch(court,court_index,num)