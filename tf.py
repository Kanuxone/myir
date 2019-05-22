import math
from itertools import groupby


def dfFunctions(word,dicted,N,word_tf ):
    df = {}
    for i in word:
        df[i] = {len(dicted[i])}
    idf = idfFunctions(word,df,N)
    tfIdf = tfIdfFunctions(dicted,word,idf,word_tf)
    dict_sumtf={}
    sum =0.0
    for i in range(0,100):
       for j in  word:
           sum = sum + tfIdf[j][i]
       dict_sumtf[i] = sum
       sum=0
    rank = sorted(dict_sumtf.items(), key=lambda kv: kv[1], reverse=True)
    return rank 


def idfFunctions(word,df,N):
    idf = {}
    for i in word:
        for j in df[i]:
            idf[i] = math.log(N/j,10)
    return idf

def tfIdfFunctions(dicted,word,idf,word_tf):
    tfIdf = {}
    for i in word:
        for j in range(0,len(word_tf)):
            a = word_tf [j]
            print(a)
            if i in tfIdf:
                tfIdf[i][j] = a.count(i)*idf[i]
            else:
                tfIdf[i] =  j
                tfIdf[i] = {j : a.count(i)*idf[i]}
    return tfIdf