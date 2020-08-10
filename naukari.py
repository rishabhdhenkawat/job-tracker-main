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


def naukari(mongo):
    url_list = []
    from selenium.webdriver.chrome.options import Options

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    #for i in range(1,2):
    driver.get('https://www.naukri.com/jobs-in-india-1?jobAge=1');
    time.sleep(5)
    driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[2]/section[2]/div[1]/div/span[2]/p').click()
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[2]/section[2]/div[1]/div/span[2]/ul/li[2]').click()
    time.sleep(5)
    pg = driver.page_source
    bs = BeautifulSoup(pg, "html5lib")
    for j in range(0, len(bs.find_all('a',{'class':'title fw500 ellipsis'}))):
            url_list.append(bs.find_all('a',{'class':'title fw500 ellipsis'})[j].get('href'))

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

    for url in tqdm(url_list):
        if mongo.check_duplicate("Naukari", hash(url)):
            continue;

        driver.get(url)
        pg = driver.page_source
        bs = BeautifulSoup(pg, "html5lib")
        time.sleep(2)

        try:
            Title.append(bs.find('h1', {'class':{'jd-header-title'}}).text)
        except:
            continue;
        try:
            Company.append(bs.find('a', {'class':{'pad-rt-8'}}).text)
        except:
            Title.pop()
            continue;
        try:
            post= driver.find_element_by_xpath('//*[@id="root"]/main/div[2]/div[2]/section[1]/div[2]/div[1]/span[1]/span')
            if post.text.split(" ")[1] == 'minutes' or post.text.split(" ")[1] == 'minute':
                Posted_On.append(datetime.now()-timedelta(minutes = int(post.text.split(" ")[0])))
            elif post.text.split(" ")[1] == 'hours' or post.text.split(" ")[1] == 'hour':
                Posted_On.append(datetime.now()-timedelta(hours = int(post.text.split(" ")[0])))
            elif post.text.split(" ")[1] == 'days' or post.text.split(" ")[1] == 'day':
                Posted_On.append(datetime.now()-timedelta(days = int(post.text.split(" ")[0])))
            else:
                Posted_On.append(datetime.now())
        except:
            Posted_On.append(datetime.now())
        try:
            Location.append(bs.find('div', {'class':{'loc'}}).text.replace("View More",""))
        except:
            Location.append("NA")
        try:
            Type.append(driver.find_element_by_xpath('//*[@id="root"]/main/div[2]/div[2]/section[2]/div[2]/div[4]/span/span').text)
        except:
            Type.append("Full Time")
        try:
            Industry.append(driver.find_element_by_xpath('//*[@id="root"]/main/div[2]/div[2]/section[2]/div[2]/div[2]/span').text)
        except:
            Industry.append("NA")
        try:
            Departments.append(driver.find_element_by_xpath('//*[@id="root"]/main/div[2]/div[2]/section[2]/div[2]/div[3]/span').text.split(", "))
        except:
            Departments.append(["NA"])
        try:
            Experience.append(bs.find('div', {'class':{'exp'}}).text)
        except:
            Experience.append("NA")
        try:
            Description.append(bs.find('div', {'class':{'dang-inner-html'}}).text)
        except:
            Description.append("NA")
        try:
            skills = []
            skill = bs.find_all('a', {'class':{'chip non-clickable'}})
            if skill is not None:
                for s in skill:
                    n = s.find('span')
                    skills.append(n.text)
            Skills.append(skills)
        except:
            Skills.append(["NA"])

        Scraped_Datetime.append(datetime.now())
        URL.append(url)
        Portal.append("Naukari")
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
    return
