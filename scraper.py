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
from linkedin import linkedin
from times import timesjobs
from internshala import internshala
from naukari import naukari
from monster import monster
from indeed import indeed
from mongo_class import *
import sys
import threading
sys.stdout.flush()

def auto_scraping(mongo, break_time = None, sleep_time = 10, linkedin_loop = 2, timesjobs_loop = 2, internshala_loop = 1440, naukari_loop = 3, indeed_loop = 2, monster_loop = 2):
    print("Starting auto-scraper!", flush=True)
    start_time = datetime.now()

    next_linkedin = datetime.now()
    next_timesjobs = datetime.now()
    next_internshala = datetime.now()
    next_naukari = datetime.now()
    next_indeed = datetime.now()
    next_monster = datetime.now()

    while True:
        if break_time != None and datetime.now() > start_time + timedelta(minutes = break_time):
            print("Quiting auto scraping", flush=True)
            break;

        if next_linkedin <=datetime.now():
            print("Starting Linkedin Scraper", flush=True)
            linkedin(mongo)
            print("Linekdin Scraping done", flush=True)
            next_linkedin += timedelta(minutes = linkedin_loop)

        if next_timesjobs <= datetime.now():
            print("Starting Times Jobs Scraper", flush=True)
            timesjobs(mongo)
            print("Times Jobs Scraping done", flush=True)
            next_timesjobs += timedelta(minutes = timesjobs_loop)

        if next_internshala <= datetime.now():
            print("Starting Internshala Scraper", flush=True)
            internshala(mongo)
            print("Internshala Scraping done", flush=True)
            next_internshala += timedelta(minutes = internshala_loop)

        if next_indeed <= datetime.now():
            print("Starting Indeed Scraper", flush=True)
            indeed(mongo)
            print("Indeed Scraping done", flush=True)
            next_indeed += timedelta(minutes = indeed_loop)

        if next_naukari <= datetime.now():
            print("Starting Naukari Scraper", flush=True)
            naukari(mongo)
            print("Naukari Scraping done", flush=True)
            next_naukari += timedelta(minutes = naukari_loop)

        if next_monster <= datetime.now():
            print("Starting Monster Scraper", flush=True)
            monster(mongo)
            print("Monster Scraping done", flush=True)
            next_monster += timedelta(minutes = monster_loop)

        print("Taking break of ", str(sleep_time) ," minutes")
        time.sleep(sleep_time)


def linkedin_thread(mongo, t=2):
    while True:
        print("Starting Linkedin Scraper", flush=True)
        linkedin(mongo)
        print("Linekdin Scraping done", flush=True)
        time.sleep(int(t)*60)
    return

def times_thread(mongo, t=2):
    while True:
        print("Starting Times Jobs Scraper", flush=True)
        timesjobs(mongo)
        print("Times Jobs Scraping done", flush=True)
        time.sleep(int(t)*60)
    return

def internshala_thread(mongo, t=1440):
    while True:
        print("Starting Internshala Scraper", flush=True)
        internshala(mongo)
        print("Internshala Scraping done", flush=True)
        time.sleep(int(t)*60)
    return

def naukari_monster_thread(mongo, t=5):
    while True:
        print("Starting Naukari Scraper", flush=True)
        naukari(mongo)
        print("Naukari Scraping done", flush=True)
        print("Starting Monster Scraper", flush=True)
        monster(mongo)
        print("Monster Scraping done", flush=True)
        #time.sleep(int(t)*60)
    return

def indeed_thread(mongo, t=7):
    while True:
        print("Starting Indeed Scraper", flush=True)
        indeed(mongo)
        print("Indeed Scraping done", flush=True)
        time.sleep(int(t)*60)
    return

def monster_thread(mongo, t=4):
    while True:
        print("Starting Monster Scraper", flush=True)
        monster(mongo)
        print("Monster Scraping done", flush=True)
        time.sleep(int(t)*60)
    return


def auto_scraping2(mongo):
    print("Starting auto-scraper!", flush=True)

    t1 = threading.Thread(target=linkedin_thread, args=(mongo,))
    t2 = threading.Thread(target=times_thread, args=(mongo,))
    t3 = threading.Thread(target=internshala_thread, args=(mongo,))
    t4 = threading.Thread(target=naukari_monster_thread, args=(mongo,))
    t5 = threading.Thread(target=indeed_thread, args=(mongo,))
    #t6 = threading.Thread(target=monster_thread, args=(mongo,))

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    #t6.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    #t6.join()

    print("Quitting scraper")

    return

if __name__ == "__main__":
    jl = MongoDb(collection="testing3")
    #jl.delete_all()
    auto_scraping2(jl)
    #print(jl.fetch_some(5))
    #jl.disconnect()
    #print(jl.check_duplicate("M",1926248514))
    #auto_scraping(jl)
    #jl.fetch_some(100)
    #jl.fetch_by_hours(5)
