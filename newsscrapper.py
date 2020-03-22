import urllib.request
from bs4 import BeautifulSoup
import time
from newspaper import Article
import nltk
import sqlite3
from sqlite3 import Error
import re

#it is used to search words
def find_word(text):
    search=['surge','acquisitions','IPO','coronavirus','covid-19']
    for i in search:
        result=re.findall('\\b'+i+'\\b',text,flags=re.IGNORECASE)
        if len(result)>0:
            print(f"{i} found in news")
            return;

# it is used to establish a sqllite connection
def sql_connection():
    try:
        con=sqlite3.connect('mydatabase11.db') # it is used to connect to  a data base i.e mydatabase.db file
        # this file is created on disk . if we want to create the db on ram then we have to use connect(:memory)
        print("connection is established...")
        return con
    except Error:
        print("Error!")

# it is used to create a table
def sql_create_table(con,tname):
    try:
        mcur=con.cursor() # it gives the cursor object that is used to execute the sqlite statemsnts    
        mcur.execute(f"CREATE TABLE {tname}(title text PRIMARY KEY,summary text )")
        con.commit()
        # in order to drop the table just write DROP TABLE tablename inside execute.
    except Error:
        print("Error!")

# it used to insert data into the table
def sql_insert(con,entities,tname):
    try:
        mcur=con.cursor() # it gives the cursor object that is used to execute the sqlite statemsnts    
        mcur.execute(f"INSERT INTO {tname}(title,summary)VALUES(?,?)",entities)
        con.commit()
    except Error:
        print("Error!")

# it used to extract data from the table and display it also checks for exact word
def sql_select(con,tname):
    try:
        mcur=con.cursor() # it gives the cursor object that is used to execute the sqlite statemsnts    
        print("title:")
        mcur.execute(f"SELECT title from {tname}")
        rows=mcur.fetchall()
        for row in rows:
            # checks for the exact word
            print(row)
        print("summary:")
        mcur.execute(f"SELECT summary from {tname}")
        rows=mcur.fetchall()
        for row in rows:
            find_word(row[0])
            print(row)
    except Error:
        print("Error!")

count=0 # number of news to be taken from the page. I have taken 2 news.
nltk.download('punkt')
rcon=sql_connection()
url='https://news.google.com/' #url of the web page

page=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}) 
pdata=urllib.request.urlopen(page).read()

soup=BeautifulSoup(pdata,'lxml')
j=soup.find_all("a",{"class":"VDXfz"})

for i in j:

    count=count+1; # number of news to be scraped
    l=i['href'].split('./') # it is used because. i am not getting the full path of the url. it is giving relative path.so
    lnk=url+l[1]    # to make it full path iam adding header to the relative  path.

    myarticle=Article(lnk,language='en')
    myarticle.download()
    myarticle.parse()
    myarticle.nlp()
    
    entities=(myarticle.title,myarticle.summary)
    tname=f"news{count}" # table name
    #print(1)
    sql_create_table(rcon,tname)
    #print(2)
    sql_insert(rcon,entities,tname)
    #print(3)
    if count==3:
        break
    time.sleep(5)

# it is to print the title and summary of the main and sub news by exacting from the table.
for i in range(count-1):
    sql_select(rcon,f"news{i+1}")
    time.sleep(10)

