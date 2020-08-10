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


def internshala(mongo):
    url = 'https://internshala.com/internships'
    response = requests.get(url)
    pg = response.content
    bs = BeautifulSoup(pg, "html5lib")
    last_page = bs.find("span", {"id":"total_pages"}).text

    url_list = []
    for i in tqdm(range(1, 26)):
        url = 'https://internshala.com/internships/page-' + str(i)
        response = requests.get(url)
        pg = response.content
        bs = BeautifulSoup(pg, "html5lib")
        for j in range(0, len(bs.find_all("div", {"class":"internship_meta"}))):
            url_list.append("https://internshala.com" + bs.find_all("div", {"class":"internship_meta"})[j].find("a").get("href"))

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

    for url in tqdm(url_list[:1000]):
        if mongo.check_duplicate("Internshala", hash(url)):
            continue;

        response = requests.get(url)
        pg = response.content
        bs = BeautifulSoup(pg, "html5lib")

        try:
            Title.append(bs.find("span", {"class":"profile_on_detail_page"}).text)
        except:
            continue;
        try:
            Company.append(bs.find("div", {"class":"heading_6 company_name"}).text.replace("\n","").replace("  ",""))
        except:
            Title.pop()
            continue;
        try:
            Location.append(bs.find("div", {"id":"location_names"}).text.replace("\n","").replace("  ",""))
        except:
            Location.append("NA")
        try:
            Description.append(bs.find("div", {"class":"internship_details"}).text.replace("\n"," ").replace("  ","").replace("Apply now","").replace("http://www."," ").replace(".com/"," "))
        except:
            Description.append("NA")
        try:
            skill_check = 0
            for i in bs.find_all("div", {"class":"section_heading heading_5_5"}):
                if i.text == "Skill(s) required":
                    skill_check = 1
            skills = ["NA"]
            if skill_check == 1:
                skills.pop()
                for j in range(0, len(bs.find("div", {"class":"round_tabs_container"}).find_all("span"))):
                    skills.append(bs.find_all("span", {"class":"round_tabs"})[j].text)
            Skills.append(skills)
        except:
            Skills.append(["NA"])

        Posted_On.append(datetime.now())
        Type.append("Internship")
        Experience.append("Not Applicable")
        Industry.append("NA")
        Departments.append(["NA"])
        Scraped_Datetime.append(datetime.now())
        URL.append(url)
        Portal.append("Internshala")
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
