from flask import Flask, render_template, request
import requests
from lxml import html
from bs4 import BeautifulSoup
import nltk
import pandas as pd
import io
import re
import json
import fnmatch
import tf
from time import time as sec
from nltk.corpus import stopwords
nltk.download('stopwords')

app = Flask(__name__)
mydict = []
df = pd.read_csv('URL.csv')
j = open('dictin100.json')
mydict = json.load(j)
j.close()


mydict2 = {}
df = pd.read_csv('URL.csv')
j = open('dictpo100.json')
mydict2 = json.load(j)
j.close()

@app.route('/')
def hello():
   return render_template('index.html')

@app.route('/Rank', methods =["POST" , "GET"])
def rank ():
  list_text =[]
  urlrank = []
  word_rank = []
  if request.method == "POST":
    result = request.args
    word = request.form["word"]
    list_text = splitword(word)
    count = 0
    for i in list_text:
      if i in mydict.keys():
        word_rank.append(i)
        count +=1 
    if count > 0:     
      ranktf = tf.dfFunctions(word_rank,wordhash,100,word_tf)
      for i in range(0,len(ranktf)):
        urlrank.append(df['url'][ranktf[i][0]])
    else:
      ranktf =[[0,"NOT FOUND"]]
    return render_template("Rank.html",rank1 = ranktf,urlrank = urlrank, word = word)

@app.route('/test', methods =["POST" , "GET"])
def wild ():
  result = request.args
  word = request.form["wild"]
  urlfil = []
  text = checkword(word)
  if text == "No Word":
    urlfil.append("NOT FOUNT")
  else:
      for k in text[1]:
        urlfil.append(df['url'][k])
  return render_template("test.html",urlfil = urlfil,listword = list_fil,word = word)
      


@app.route('/result', methods = ['POST','GET'])	
def result	():	
  if request.method == "POST":
    result = request.args
    word = request.form["word"]
    

    list_text =[]
    list_text = splitword(word)

    
    count = 0
    for i in list_text:
      if i in mydict2.keys():
        count +=1
    

    if word.count('*') != 0:
      global list_fil 
      urlfil =[]
      dict_fil={}
      list_fil = []
      list_filtered = splitword(word)
      print(list_filtered)
      for i in list_filtered:
        filtered = fnmatch.filter(mydict2,i)
        if len(filtered) > 0:
          for j in filtered:
            list_fil.append(j)
        print(list_fil)
      return render_template("test.html",listword = list_fil)
  return render_template("test.html")

def splitword(word):
  tokens = re.findall("[A-Za-z,*]+",word.lower())
  stop_words = set(stopwords.words('english'))
  listtext = []
  for i in tokens:
    if i not in stop_words:
      listtext.append(i)  
  return listtext


def checkword(text):
    for i in range(0,len(mydict)):
        if  text == mydict[i][0]:
            return mydict[i]
    return "No Word"

if __name__ == "__main__":
	app.run(debug =True)