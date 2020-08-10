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


def timesjobs(mongo):
    url_list = []

    #for i in tqdm(range(1, 2)):
    #url = 'https://www.timesjobs.com/candidate/job-search.html?from=submit&searchType=personalizedSearch&txtLocation=India&luceneResultSize=25&postWeek=3&pDate=Y&sequence=' + str(i) + '&startPage=1'
    url = 'https://www.timesjobs.com/candidate/job-search.html?from=submit&searchType=personalizedSearch&txtLocation=India&luceneResultSize=25&postWeek=3&pDate=Y&sequence=1&startPage=1'
    response = requests.get(url)
    pg = response.content
    bs = BeautifulSoup(pg, "html5lib")
    for j in range(0, len(bs.find_all("li", {"class":"clearfix job-bx wht-shd-bx"}))):
        url_list.append(bs.find_all("li", {"class":"clearfix job-bx wht-shd-bx"})[j].find("a").get("href"))

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
        if mongo.check_duplicate("Times Jobs", hash(url)):
            continue;

        response = requests.get(url)
        pg = response.content
        bs = BeautifulSoup(pg, "html5lib")

        try:
            Title.append(bs.find("h1", {"class":"jd-job-title"}).text.replace("\n","").replace("  ","").replace("\t","").replace("\"",""))
        except:
            continue;
        try:
            Company.append(bs.find("h2").text.replace("\n","").replace("  ","").replace("\t",""))
        except:
            Title.pop()
            continue;
        try:
            Location.append(bs.find("ul", {"class":"top-jd-dtl clearfix"}).find_all("li")[2].text.replace("\n","").replace("\t","").split("  ")[4])
        except:
            Location.append("NA")
        try:
            Posted_On.append(datetime.strftime(bs.find("div", {"class":"jd-header wht-shd-bx"}).find_all("strong")[1].text[10:], '%d %b, %Y'))
        except:
            Posted_On.append(datetime.now())
        Type.append("NA")
        Industry.append("NA")
        Departments.append("NA")
        try:
            for i in bs.find("div", {"class":"job-basic-info"}).find_all("li", {"class":"clearfix"}):
                if i.text.split()[0] == "Job":
                    Departments.pop()
                    Departments.append([" ".join(i.text.split()[2:])])
                elif i.text.split()[0] == "Industry:":
                    Industry.pop()
                    Industry.append(" ".join(i.text.split()[1:]))
                elif i.text.split()[0] == "Employment":
                    Type.pop()
                    Type.append(" ".join(i.text.split()[2:]))
        except:
            pass
        try:
            Experience.append(bs.find("ul", {"class":"top-jd-dtl clearfix"}).find_all("li")[0].text.replace("\n","").replace("\t","").split("  ")[3] + " years")
        except:
            Experience.append("NA")
        try:
            Description.append(bs.find("div", {"class":"jd-desc job-description-main"}).text.replace("\n","").replace("\t","")[31:])
        except:
            Description.append("NA")
        try:
            skills = []
            for i in bs.find_all("span", {"class":"jd-skill-tag"}):
                skills.append(i.text[:-1].replace("\"",""))
            Skills.append(skills)
        except:
            skills.append(["NA"])

        Scraped_Datetime.append(datetime.now())
        URL.append(url)
        Portal.append("Times Jobs")
        Portal_Id.append(hash(url))

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
