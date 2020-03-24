import urllib.request
from bs4 import BeautifulSoup
import time
from newspaper import Article
import nltk
import sqlite3
from sqlite3 import Error
import re
import pandas as pd
from urllib.request import build_opener, HTTPCookieProcessor

#it is used to search words
def find_word(soup1):
    search=['surge','acquisitions','IPO','coronavirus','covid-19']
    for i in search:
        result=re.findall('\\b'+i+'\\b',soup1.text,flags=re.IGNORECASE)
        if len(result)>0:
            print(f"{i} found in news")
            return;

# it is used to establish a sqllite connection
def sql_connection():
    try:
        con=sqlite3.connect('mydatabase10.db') # it is used to connect to  a data base i.e mydatabase.db file
        # this file is created on disk . if we want to create the db on ram then we have to use connect(:memory)
        print("connection is established...")
        return con
    except Error:
        print("Error!")

# it is used to create a table
def sql_create_table(con,tname):
    try:
        mcur=con.cursor() # it gives the cursor object that is used to execute the sqlite statemsnts    
        mcur.execute(f"CREATE TABLE {tname}(title text PRIMARY KEY,summary text,publishdate text)")
        con.commit()
        # in order to drop the table just write DROP TABLE tablename inside execute.
    except Error:
        print("Error!")

# it used to insert data into the table
def sql_insert(con,entities,tname):
    try:
        mcur=con.cursor() # it gives the cursor object that is used to execute the sqlite statemsnts    
        mcur.execute(f"INSERT INTO {tname}(title,summary,publishdate)VALUES(?,?,?)",entities)
        con.commit()
    except Error:
        print("Error!")

# it used to extract data from the table and display it also checks for exact word
def sql_select(con,tname):
    try:
        df=pd.read_sql_query(f"select * from {tname} limit 5;",con)
        print(df)
    except Error:
        print("Error!")

count=1 # number of news to be taken from the page. I have taken 2 news.
nltk.download('punkt')
rcon=sql_connection()
sql_create_table(rcon,"main_news")
sql_create_table(rcon,"sub_news")

url='https://news.google.com/' #url of the web page

page=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}) 
pdata=urllib.request.urlopen(page).read()

soup=BeautifulSoup(pdata,'lxml')

main=soup.find("main",{"class":"HKt8rc CGNRMc"})
main_news=main.find_all("h3",{"class":"ipQwMb ekueJc gEATFF RD0gLb"})
sub_news=main.find_all("h4",{"class":"ipQwMb ekueJc gEATFF RD0gLb"})

murl='https://news.google.com' 

print("<<............................................Main News Collecting...................................................>>")
for j in main_news:
    if count<=5:
        i=j.find("a",href=True)
        l=i['href'].split('.')
        lnk=murl+l[1]
        try:
            page1=urllib.request.Request(lnk,headers={'User-Agent':'Mozilla/5.0'}) 
            pdata1=urllib.request.urlopen(page1).read()
            soup1=BeautifulSoup(pdata1,'lxml')
            find_word(soup1)

            myarticle=Article(lnk,language='en')
            time.sleep(3)
            myarticle.download()
            myarticle.parse()
            myarticle.nlp()
            
            entities=(myarticle.title,myarticle.summary,myarticle.publish_date)
            sql_insert(rcon,entities,"main_news")
        except Exception as e:
            print("")
        
        count=count+1
        time.sleep(5)

print("<<............................................Sub News Collecting...................................................>>")
for j in sub_news:
    if count>1:
        i=j.find("a",href=True)
        l=i['href'].split('.')
        lnk=murl+l[1]
        try:
            page1=urllib.request.Request(lnk,headers={'User-Agent':'Mozilla/5.0'}) 
            pdata1=urllib.request.urlopen(page1).read()
            soup1=BeautifulSoup(pdata1,'lxml')
            find_word(soup1)

            myarticle=Article(lnk,language='en')
            time.sleep(3)
            myarticle.download()
            myarticle.parse()
            myarticle.nlp()
            
            entities=(myarticle.title,myarticle.summary,myarticle.publish_date)
            sql_insert(rcon,entities,"sub_news")
        except Exception as e:
            print("")
        
        count=count-1
        time.sleep(10)

sql_select(rcon,"main_news")
sql_select(rcon,"sub_news")
