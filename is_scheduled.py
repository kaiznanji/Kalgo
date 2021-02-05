# In this file we will check if each company's grant of stocks is part of a regularly scheduled event
#  (incentive bonus, performance award, yearly grant, etc)

# Import libraries
from joblib import load
import bs4 as bs
import requests
import datetime as dt


def scheduled():
    dictionary = load("links")
    
    for key,value in dictonary.items():
        



scheduled()