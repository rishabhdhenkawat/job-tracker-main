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



def indeed(mongo):
    url_list = []
    for i in tqdm(range(0, 3)):
        url = 'https://www.indeed.co.in/jobs?q=fresher&l=India&fromage=1&start=' + str(i*10)
        response = requests.get(url)
        pg = response.content
        bs = BeautifulSoup(pg, "html5lib")
        for j in range(0, len(bs.find_all("h2", {"class":"title"}))):
            url_list.append(bs.find_all("h2", {"class":"title"})[j].find("a").get("href"))

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
        if mongo.check_duplicate("Indeed", hash(url)):
            continue;

        response = requests.get("https://www.indeed.co.in" + url)
        pg = response.content
        bs = BeautifulSoup(pg, "html5lib")

        try:
            Title.append(bs.find('h3', {'class':{'icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title'}}).text)
        except:
            continue;
        try:
            Company.append(bs.find('div', {'class':{'icl-u-lg-mr--sm icl-u-xs-mr--xs'}}).text)
        except:
            Title.pop()
            continue;
        try:
            Location.append(bs.find("div", {"class":"jobsearch-InlineCompanyRating icl-u-xs-mt--xs icl-u-xs-mb--md"}).text.split("-")[-1])
        except:
            Location.append("NA")
        try:
            Description.append(bs.find('div', {'id':{'jobDescriptionText'}}).text)
        except:
            Description.append("NA")
        try:
            if "Today" or "Just" in list(bs.find("div", {"class":"jobsearch-JobMetadataFooter"}).text.split()):
                Posted_On.append(datetime.now())
            elif "day" in list(bs.find("div", {"class":"jobsearch-JobMetadataFooter"}).text.split()):
                Posted_On.append(datetime.now() - timedelta(minutes=1440))
            else:
                Posted_On.append(datetime.now())
        except:
            Posted_On.append(datetime.now())

        Portal_Id.append(hash(url))
        Type.append("Full Time")
        Industry.append("NA")
        Departments.append(["NA"])
        Experience.append("NA")
        Skills.append(["NA"])
        Scraped_Datetime.append(datetime.now())
        URL.append("https://www.indeed.co.in" + url)
        Portal.append("Indeed")

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
