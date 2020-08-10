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
from mongo_class import *


def linkedin(mongo):
    url = 'https://www.linkedin.com/jobs/search?location=India&trk=homepage-jobseeker_jobs-search-bar_search-submit&sortBy=DD&f_TP=1&redirect=false&position=1&pageNum=0'
    response = requests.get(url)
    pg = response.content
    bs = BeautifulSoup(pg,"html5lib")
    try:
        postings = bs.find_all("a", {"class":"result-card__full-card-link"})
    except:
        return
    url_list = []
    for i in postings:
        url_list.append(i.get("href"))

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
        if count > 0:
            if mongo.check_duplicate("LinkedIn", hash(url)):
                continue;

        response = requests.get(url)
        pg = response.content
        bs = BeautifulSoup(pg, "html5lib")

        try:
            Title.append(bs.find("h2", {"class":"topcard__title"}).text)
        except:
            try:
                Title.append(bs.find("h1", {"class":"jobs-top-card__job-title t-24"}).text)
            except:
                continue;
        try:
            if len(bs.find_all("a", {"class":"topcard__org-name-link topcard__flavor--black-link"})) > 0:
                Company.append(bs.find("a", {"class":"topcard__org-name-link topcard__flavor--black-link"}).text)
            elif len(bs.find_all("span", {"class":"topcard__flavor"})) > 0:
                Company.append(bs.find("span", {"class":"topcard__flavor"}).text)
        except:
            Title.pop()
            continue;
        try:
            posted_time = bs.find("span", {"class":"topcard__flavor--metadata posted-time-ago__text posted-time-ago__text--new"}).text
            if posted_time.split(" ")[1] == "minutes" or posted_time.split(" ")[1] == "minute":
                Posted_On.append(datetime.now() - timedelta(minutes = int(posted_time.split(" ")[0])))
            elif posted_time.split(" ")[1] == "hour" or posted_time.split(" ")[1] == "hours":
                Posted_On.append(datetime.now() - timedelta(minutes = int(posted_time.split(" ")[0])*60))
            else:
                Posted_On.append(datetime.now())
        except:
            Posted_On.append(datetime.now())
        try:
            Location.append(bs.find("span", {"class":"topcard__flavor topcard__flavor--bullet"}).text)
        except:
            Location.append("NA")

        Type.append("NA")
        Experience.append("NA")
        Industry.append("NA")
        Departments.append(["NA"])
        try:
            criteria = bs.find_all("li", {"class":"job-criteria__item"})
            for i in criteria:
                c = i.find("h3", {"class":"job-criteria__subheader"}).text
                if c == "Employment type":
                    Type.pop()
                    Type.append(i.find("span", {"class":"job-criteria__text job-criteria__text--criteria"}).text)
                elif c == "Seniority level":
                    Experience.pop()
                    Experience.append(i.find("span", {"class":"job-criteria__text job-criteria__text--criteria"}).text)
                elif c == "Industries":
                    Industry.pop()
                    Industry.append(i.find("span", {"class":"job-criteria__text job-criteria__text--criteria"}).text)
                elif c == "Job function":
                    Departments.pop()
                    Departments.append(i.find("span", {"class":"job-criteria__text job-criteria__text--criteria"}).text.split(", "))
        except:
            pass
        try:
            Description.append(bs.find("div", {"class":"show-more-less-html__markup show-more-less-html__markup--clamp-after-5"}).text)
        except:
            Description.append("NA")

        Skills.append(["NA"])
        Scraped_Datetime.append(datetime.now())
        URL.append(url)
        Portal.append("LinkedIn")
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
    count=count+1
    return
