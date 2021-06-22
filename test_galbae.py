from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import os, sys, time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import smtplib
from email.mime.text import MIMEText
from datetime import datetime



def sendmail(result):
    now = datetime.now()
    current =  ("%s-%s-%s %s시" %(now.year, now.month, now.day, now.hour))
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('ID','PASSWORD')

    if len(result) == 0:
        msg = MIMEText('모든 키워드가 3페이지 이내에 존재함.')
    else:
        contents = result[0]
        for i in range(1, len(result)):
            contents += '\n' + result[i]
        msg = MIMEText(contents)

    msg['Subject'] = '제목 :'+str(current)+' .'
    s.sendmail("보내는사람", "받는사람", msg.as_string())
    s.quit()


def getData():
    df = pd.read_excel("keyword.xlsx")
    keywordList = df["키워드"]
    return keywordList

def process(keywordList):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome('크롬드라이버 경로', options=options)
    driver.maximize_window()

    driver.get("https://ad.search.naver.com/search.naver?where=ad&query=&x=24&y=20")

    host = "찾고자 하는 URL"
    result = []
    for i in range(len(keywordList)):
        search = driver.find_element_by_id("nx_query")
        search.send_keys(keywordList[i])
        search.send_keys(Keys.ENTER)
        
        driver.implicitly_wait(1)

        pagelen = driver.find_element_by_class_name("paginate")

        if len(pagelen.text) < 13:
            driver.find_element_by_id("nx_query").clear()
            continue
        
        flag = 0
        for j in range(2):
            urlList = driver.find_elements_by_class_name("url")
            for link in urlList:
                if link.text == host:
                    flag = 1
                    break
            driver.find_element_by_class_name("next").click()
            driver.implicitly_wait(1)

        if flag == 0:
            result.append(keywordList[i]+str(": 3페이지 이내에 없음." ))
            print(keywordList[i]+str(": 3페이지 이내에 없음." ))

        driver.find_element_by_id("nx_query").clear()

    sendmail(result)
    driver.quit()
process(getData())