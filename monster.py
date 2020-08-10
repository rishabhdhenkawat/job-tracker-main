import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import numpy as np
from datetime import datetime
from datetime import timedelta
import time
import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
import json


def monster(mongo):
    url_list = []
    from selenium.webdriver.chrome.options import Options

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    #driver = webdriver.Chrome(r'C:\Users\rdhen\OneDrive\Desktop\chromedriver.exe')
    driver.get('https://www.monsterindia.com/srp/results?sort=2&limit=20&locations=india');
    time.sleep(5)
    pg = driver.page_source
    bs = BeautifulSoup(pg, "html5lib")
    for j in range(0, len(bs.find_all("h3", {"class":"medium"}))):
        try:
            url_list.append(bs.find_all("h3", {"class":"medium"})[j].find("a").get("href"))
        except:
            continue;

    Portal_Id = []
    Title = []
    Company = []
    Location = []
    Posted_On = []
    Type = []
    Experience = []
    Industry = []
    Departments = []
    Description = []
    Skills = []
    Scraped_Datetime = []
    URL = []
    Portal = []
    count=0
    for url in tqdm(url_list):

        if count>0:
            if mongo.check_duplicate("Monster", hash(url)):
                continue;

        driver.get("https:" + url);
        time.sleep(5)
        pg = driver.page_source
        bs = BeautifulSoup(pg, "html5lib")

        try:
            Title.append(bs.find("div", {"class":"job-tittle detail-job-tittle"}).find("h1").text)
        except:
            continue;
        try:
            Company.append(bs.find("div", {"class":"job-tittle detail-job-tittle"}).find("span").text)
        except:
            Title.pop()
            continue;
        try:
            Location.append(bs.find("div", {"class":"col-xxs-12 col-sm-5 text-ellipsis"}).text.strip())
        except:
            Location.append("NA")
        try:
            post = bs.find_all("span", {"class":"posted seprator pLR-10"})[0]
            if post.text.split()[3] == 'minutes' or post.text.split()[3] == 'minute':
                if post.text.split(" ")[2] == "a":
                    Posted_On.append(datetime.now()-timedelta(minutes = 1))
                else:
                    Posted_On.append(datetime.now()-timedelta(minutes = int(post.text.split(" ")[2])))
            elif post.text.split()[3] == 'hours' or post.text.split()[3] == 'hour':
                if post.text.split(" ")[2] == "an":
                    Posted_On.append(datetime.now()-timedelta(minutes = 60))
                else:
                    Posted_On.append(datetime.now()-timedelta(hours = int(post.text.split(" ")[2])))
            else:
                Posted_On.append(datetime.now())
        except:
            Posted_On.append(datetime.now())
        try:
            if bs.find('span', {'class':'exp'}).text.strip() == "":
                Experience.append("NA")
            else:
                Experience.append(bs.find('span', {'class':'exp'}).text.strip())
        except:
            Experience.append("NA")
        Industry.append("NA")
        Departments.append(["NA"])
        Skills.append(["NA"])
        try:
            criteria = bs.find_all("div", {"class":"job-detail-list"})
            if len(criteria) > 0:
                for i in criteria:
                    c = i.find("h3").text
                    if c == "Industry:":
                        Industry.pop()
                        Industry.append(i.find("p", {"class":"jd-text"}).text.strip().encode("ascii", errors="ignore").decode("utf-8").replace("  ","").replace("\n"," "))
                    elif c == "Skills:":
                        Skills.pop()
                        skills = []
                        for sk in i.find("p", {"class":"color-grey-black fs-14 medium"}).find_all("span"):
                            skills.append(sk.text.encode("ascii", errors="ignore").decode("utf-8").strip())
                        Skills.append(skills)
                    elif c == "Function:":
                        Departments.pop()
                        Departments.append(i.find("p", {"class":"jd-text"}).text.encode("ascii", errors="ignore").decode("utf-8").strip().replace("  ","").replace("\n","").split(","))
        except:
            pass
        try:
            Description.append(bs.find('div', {'class':'card-panel job-description-content'}).text.encode("ascii", errors="ignore").decode("utf-8").strip().replace("\t","").replace("\n",""))
        except:
            Description.append("NA")

        Type.append("Full Time")
        Scraped_Datetime.append(datetime.now())
        URL.append("https:" + url)
        Portal.append("Monster")
        Portal_Id.append(hash(url))

    driver.quit();

    data = {"Portal_Id": Portal_Id,
    "Title": Title,
    "Company": Company,
    "Location": Location,
    "Posted_On": Posted_On,
    "Type": Type,
    "Experience": Experience,
    "Industry": Industry,
    "Departments": Departments,
    "Description": Description,
    "Skills" : Skills,
    "Scraped_Datetime" : Scraped_Datetime,
    "URL": URL,
    "Portal": Portal}
    data_df = pd.DataFrame(data)

    if data_df.empty:
        return
    else:
        mongo.insert_df(data_df)
    count = count + 1
    return
