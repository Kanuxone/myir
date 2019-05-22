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

# เอาไว้ render ข้อมูล
class Result:
    def __init__(self,word=None,value=None,file=None):
        self.word = word
        self.value = value
        self.file = file
      
        

# router สำหรับรับ path
app = Flask(__name__)
@app.route('/')
def hello():
   return render_template('index.html')

@app.route('/result',methods=['POST'])
def showResult():
    word=[]

    dateStart = asc(loc(sec()))
    if request.method=='POST':
        word = request.form['word'].lower().split(" ")

    result= []

    timeStart = sec()
    for i in word:
        temp = search(i)
    timeEnd = sec()
    timeSeq = timeEnd - timeStart

    inter2 = []
    timeStart = sec()
    for i in word:
        inter = []
        inter.append(i)
        x = list(intersect(inter))
        if len(inter) != 0:
          inter2.append(x) 
        else:
          inter2.append("No intersect because word not found!!")
    timeEnd = sec()
    timePos = timeEnd - timeStart

    timeStart = sec()
    for i in word:
        temp = binary.get(i)
    timeEnd = sec()
    timeBi = timeEnd - timeStart
    
    timeStart = sec()
    for i in word:
        temp = hashTable.search(i)
        if temp != None:
            result.append(Result(i,temp.value,temp.file))
        else:
            result.append(Result(i))
    timeEnd = sec()
    timeHash = timeEnd - timeStart
    dateEnd = asc(loc(sec()))

##### ส่งค่าไปโชว์ ######
    return render_template('result.html',result=result,inter=inter2,timeSeq=timeSeq,timeBi=timeBi,timeHash=timeHash,dateStart=dateStart,dateEnd=dateEnd,size=hashTable.size)


# โหลดข้อมูล จาก ไฟล์ csv
df = pd.read_csv('Web.csv')
url=[]
for line in range(len(df)):
  url.append(df['Colum'][line])
# class สำหรับเก็บข้อมูล
class Data:
    def __init__(self,id,word,file):
        self.id = id
        self.order=order
        self.word = word
        self.posting = {id}
        self.order = [[id,order]]
        self.num = 1
        self.file = {file}

    def __str__(self):
        return self.word+ " "+ str(self.num)

class Node:
	def __init__(self, key, value, file):
            self.key = key
            self.value = value
            self.file = {file}
            self.next = None

	def __str__(self):
		return "%s %s" % (self.key, self.value)

	def __repr__(self):
		return str(self)

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


    def insert(self, key, value , file):

      index = self.hash(key)
      node = self.buckets[index]

      if node is None:
        self.buckets[index] = Node(key, value , file)
        self.size += 1
        return
      prev = node
      while node is not None:
        if(node.key==key):
          node.value=value
          node.file.add(file)
          return
        prev = node
        node = node.next
      prev.next = Node(key, value , file)
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



#### Intersect ####

# def intersec(a):
#   s1={}
#   for i in  range (0,len(a)):
#     if i == 0:
#       s1 = set(a[i][1])
#     if i < len(a)-1:
#       s1 = s1.intersection(set(a[i+1][1]))
#     if len(s1) == 0:
#       return {"NOT FOUND"}
#   return s1

def intersect(word):
  j = 0
  temp = set()
  temp2 = set()
  while True:
    if j >= len(word): 
      break 
    b = search2(word[j])
    if b != " ":
      temp = b.posting
      break
    else:
      j+=1
  while j < len(word):
      a = search2(word[j])
      if a != " ":
        temp2 = a.posting
        you = list(temp2)
        for r in range(len(you)):
          temp = set(temp.intersection(temp2))
      else:
        return "No intersect because word not found!!"
  j+=1
  return list(temp)

def binarySearchIn(l, r, x):
    array = []
    
    if r >= l: 
        mid = int(l + (r - l)/2)
        if str(array[mid].word) == x: 
            return mid           
        elif str(array[mid].word) > x: 
            return binarySearchIn(l, mid-1, x) 
        else: 
            return binarySearchIn(mid + 1, r, x)   
    else: 
        return -1
    
def searchIn(word):
  array = []
  array.append(word)
  res = binarySearchIn(0, len(array)-1,word) 
  if res == -1: 
     return "No word!!"
  else:
    return array[res]  

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
      data = urlopen(str(url[i]))
      mybytes = data.read().decode('windows-1252').lower()
      tokenizer = TreebankWordTokenizer()
      line = re.sub('[i?.,\',;:/\"<>\\%@#+-_&^$=()…—“”’*»’.``!¿\'`"â€™ï–]','', mybytes)
      arrayWord=tokenizer.tokenize(line)
      for j in range(len(arrayWord)):
        self.binary.put(arrayWord[j],1,i)
        w=self.hashTable.find(arrayWord[j])
        if(w!=None):
          self.hashTable.insert(arrayWord[j],w+1,i)
        else:
          self.hashTable.insert(arrayWord[j],1,i)
          self.sequence.append(Data(i+1,arrayWord[j],j))
        

def getData():
  l=len(url)
  thread = []
  numThread=100
  for i in range(numThread):
    thread.append(MyThread(url,(i*l)/numThread,((i+1)*l)/numThread,sequence,binary,hashTable))
    thread[i].start()
  for i in range(numThread):
    thread[i].join()


def search(word):
  for i in sequence:
    if i.word == word:
      return i
    return " "
    
# main
if __name__ == '__main__':
    sequence  = []
    hashTable = HashTable()
    binary = BinarySearchTree()

    app.run(debug=True)
