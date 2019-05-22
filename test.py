from flask import Flask,render_template,request,redirect,url_for
import re
import pandas as pd
from nltk.tokenize import TreebankWordTokenizer
from urllib.request import urlopen
import operator
import threading
from time import time as sec
from time import asctime as asc
from time import localtime as loc

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

import requests as req
from lxml import html
from bs4 import BeautifulSoup

import json
import fnmatch
import tf
import io

app = Flask(__name__)

#ข้อมูลไฟล์ json
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

hashdict ={}
j = open('dicthash100.json')
hashdict = json.load(j)
j.close()

j = open('dicthash.json')
tfdict = json.load(j)

# router สำหรับรับ path
@app.route('/')
def hello():
   return render_template('index.html')

#Position
@app.route('/position/<word>')
def showPosition(word):
    temp = hashTable.search(word)
    return render_template('position.html',word=word,position=temp.position)

#Wildcard
@app.route('/wild', methods =["POST" , "GET"])
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
  return render_template("wildcard.html",urlfil = urlfil,listword = list_fil,word = word)
    
#Rank
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
      if i in mydict2.keys():
        word_rank.append(i)
        count +=1 
    if count > 0:     
      ranktf = tf.dfFunctions(word_rank,hashdict,100,tfdict)
      for i in range(0,len(ranktf)):
        urlrank.append(df['url'][ranktf[i][0]])
    else:
      ranktf =[[0,"NOT FOUND"]]
    return render_template("Rank.html",rank1 = ranktf,urlrank = urlrank, word = word, rank = len(urlrank))

#Result
@app.route('/result',methods=['POST'])
def result():
  word=[]
  dateStart = asc(loc(sec()))
  if request.method=='POST':
    text=request.form['word']
    word=request.form['word'].lower().split(" ")

    #Wildcard
    if text.count("*") != 0:
      global list_fil 
      urlfil =[]
      dict_fil={}
      list_fil = []
      list_filtered = splitword(text)
      for i in list_filtered:
        filtered = fnmatch.filter(mydict2,i)
        if len(filtered) > 0:
          for j in filtered:
            list_fil.append(j)
      return render_template('wildcard.html',listword = list_fil)
        

    result=[]
    ###---TimeInvert---###
    timeStart = sec()
    for i in word:
        temp = hashTable.search(i)
    timeEnd = sec()
    dateEnd = asc(loc(sec()))
    timeInV = timeEnd - timeStart

    ###---TimePosition---###
    timeStart = sec()
    for i in word:
        temp = hashTable.search(i)
    timeEnd = sec()
    dateEnd = asc(loc(sec()))
    timePos = timeEnd - timeStart


    ###---TimeIntersect---###
    timeStart = sec()
    inter = intersect(word)
    if not inter:
      inter = "No Intersect"
    timeEnd = sec()
    dateEnd = asc(loc(sec()))
    timeInS = timeEnd - timeStart
      

    ###---TimeBinary---###
    timeStart = sec()
    for i in word:
        temp = binary.get(i)
    timeEnd = sec()
    dateEnd = asc(loc(sec()))
    timeBi = timeEnd - timeStart

    ###---TimeHash---###
    timeStart = sec()
    for i in word:
        temp = hashTable.search(i)
        if temp != None:
            result.append(Result(i,temp.value,temp.file)) 
        else:
            result.append(Result(i))
    timeEnd = sec()
    dateEnd = asc(loc(sec()))
    timeHash = timeEnd - timeStart
      

  return render_template('result.html',result=result,word=text,inter=inter,timePos=timePos,timeInV=timeInV,timeBi=timeBi,timeHash=timeHash,
                                        dateStart=dateStart,dateEnd=dateEnd,size=hashTable.size)

#####---!!!! ใช้กับ อัลกอ wildcard / rank / tf-idf !!!!---#####
def splitword(word):
  tokens = re.findall("[A-Za-z,*]+",word.lower())
  stop_words = set(stopwords.words('english'))
  listtext = []
  for i in tokens:
    if i not in stop_words:
      listtext.append(i)  
  return listtext

#####---!!!! ใช้กับ อัลกอ wildcard / rank / tf-idf !!!!---#####
def checkword(text):
    for i in range(0,len(mydict)):
        if  text == mydict[i][0]:
            return mydict[i]
    return "No Word" 


# โหลดข้อมูล จาก ไฟล์ csv
df = pd.read_csv('URL.csv')
url=[]
for line in range(len(df)):
  url.append(df['url'][line])


# Result สำหรับแสดงผล
class Result:
    def __init__(self,word=None,value=None,file=None):
        self.word = word
        self.value = value
        self.file = file

# class สำหรับเก็บข้อมูล
class Data:
    def __init__(self,id,word,file):
        self.id = id
        self.word = word
        self.num = 1
        self.file = {file}
        
    def __str__(self):
        return self.word+ " "+ str(self.num)

class Node:
	def __init__(self, key, value, file,position):
            self.key = key
            self.value = value
            self.file = {file}
            self.next = None
            self.position = [[file,position]]

	def __str__(self):
		return "%s %s" % (self.key, self.value)

	def __repr__(self):
		return str(self)

#####---Hash---#####
class HashTable:

    def __init__(self):
      self.capacity = 1000
      self.size = 0
      self.buckets = [None]*self.capacity

    def hash(self, key):
      hashsum = 0
      for idx, c in enumerate(key):
        hashsum += (idx + len(key)) ** ord(c)
        hashsum = hashsum % self.capacity
      return hashsum


    def insert(self, key, value , file, position):

      index = self.hash(key)
      node = self.buckets[index]

      if node is None:
        self.buckets[index] = Node(key, value , file, position)
        self.size += 1
        return
      prev = node
      while node is not None:
        if(node.key==key):
          node.value=value
          node.file.add(file)
          k=0
          flag=0
          while k < len(node.position):
              if(node.position[k][0]==file):
                node.position[k].append(position)
                flag=1
              k=k+1
          if(flag==0):
            node.position.insert(k,[file,position])

          self.size += 1
          return
        prev = node
        node = node.next
      prev.next = Node(key, value , file, position)
      self.size += 1

    def find(self, key):
      index = self.hash(key)
      node = self.buckets[index]
      while node is not None and node.key != key:
        node = node.next
      if node is None:
        return None
      else:
        return node.value

    def search(self, key):
      index = self.hash(key)
      node = self.buckets[index]
      while node is not None and node.key != key:
        node = node.next
      if node is None:
        return None
      else:
        return node

#####---Tree Node---#####
class TreeNode:
    def __init__(self,key,val,file,left=None,right=None,parent=None):
        self.key = key
        self.payload = val
        self.leftChild = left
        self.rightChild = right
        self.parent = parent
        self.file = {file}

    def hasLeftChild(self):
        return self.leftChild

    def hasRightChild(self):
        return self.rightChild

    def isLeftChild(self):
        return self.parent and self.parent.leftChild == self

    def isRightChild(self):
        return self.parent and self.parent.rightChild == self

    def isRoot(self):
        return not self.parent

    def isLeaf(self):
        return not (self.rightChild or self.leftChild)

    def __str__(self):
      return "%s %s" % (self.key, self.payload)

#####---Binary Search Tree---#####
class BinarySearchTree:

    def __init__(self):
        self.root = None
        self.size = 1

    def length(self):
        return self.size

    def __len__(self):
        return self.size

    def __iter__(self):
        return self.root.__iter__()

    def put(self,key,val,file):
        if self.root:
            self._put(key,val,self.root,file)
        else:
            self.root = TreeNode(key,val,file)
    def _put(self,key,val,currentNode,file):

        if key == currentNode.key:
          currentNode.payload+=val
          currentNode.file.add(file)
          return

        if key < currentNode.key:
            if currentNode.hasLeftChild():
                   self._put(key,val,currentNode.leftChild,file)
            else:
                   currentNode.leftChild = TreeNode(key,val,file,parent=currentNode)
                   self.size = self.size + 1
        else:
            if currentNode.hasRightChild():
                   self._put(key,val,currentNode.rightChild,file)
            else:
                   currentNode.rightChild = TreeNode(key,val,file,parent=currentNode)
                   self.size = self.size + 1


    def get(self,key):
       if self.root:
           res = self._get(key,self.root)
           if res:
                  return res
           else:
                  return None
       else:
           return None

    def _get(self,key,currentNode):
       if not currentNode:
           return None
       elif currentNode.key == key:
           return currentNode
       elif key < currentNode.key:
           return self._get(key,currentNode.leftChild)
       else:
           return self._get(key,currentNode.rightChild)

#####---My Thread---#####
#####---ประมวลผลการทำงานพร้อมกันหลายคำสั่ง---#####
##---สั่งงานโดยประมวลผลแบบขนานโดยเรียกใช้ฟังก์ชั่น run---#####
class MyThread(threading.Thread):
  def __init__(self,arr,lo,hi,sequence,binary,hashTable):
    threading.Thread.__init__(self)
    self.arr=arr
    self.lo=lo
    self.hi=hi
    self.sequence=sequence
    self.binary=binary
    self.hashTable=hashTable

  def run(self):
    for i in range(int(self.lo),int(self.hi)):
      web = url[i]
      resp = req.request(method = "GET",url = web)
      r = resp.content
      soup = BeautifulSoup(r, "html.parser")
      content = soup.find("body").get_text()
      arrayWord = stop_word(content)
      for j in range(len(arrayWord)):
        self.binary.put(arrayWord[j],1,i+1)
        w=self.hashTable.find(arrayWord[j])
        if(w!=None):
          self.hashTable.insert(arrayWord[j],w+1,i+1,j+1)
        else:
          self.hashTable.insert(arrayWord[j],1,i+1,j+1)
          self.sequence.append(Data(i+1,arrayWord[j],j+1))

###---Stop Word---###       
def stop_word(content):
	words = re.findall("[A-Za-z]+", content)
	s = set(stopwords.words('english'))
	stopW = []
	for selects in words:
		if selects not in s:
			stopW.append(selects)
	return stopW

###---Get Data---###
def getData():
  l=len(url)
  thread = []
  numThread=100
  for i in range(numThread):
    thread.append(MyThread(url,(i*l)/numThread,((i+1)*l)/numThread,sequence,binary,hashTable))
    thread[i].start()
  for i in range(numThread):
    thread[i].join()

###---Search---###
def search(word):
  for i in sequence:
    if(i.word == word):
      return i

#####---Intersect---#####
def intersect(word):
  j = 0
  temp = set()
  while True:
    if j >= len(word): 
      break 
    b = hashTable.search(word[j])
    if b != None:
      temp = b.file
      break
    else:
      j+=1
  while j < len(word):
      a = hashTable.search(word[j])
      if a != None:
        temp = set(temp.intersection(a.file))
      else:
        return "No Intersect"
      j+=1
  return list(temp)



# main
if __name__ == '__main__':
    sequence  = []
    hashTable = HashTable()
    binary = BinarySearchTree()
    getData()
    
    app.run(debug=True)
