from WebService import WebService
from io import TextIOWrapper
import json
from metaDataEnum import MetaDataEnum
from typing import Callable, Iterable
import re


def prograssbar(p, max):
    barsize = 1

    if p > max:
        p = max

    print('\r' + "prograss : " + '\33[5m' +
          " " + str(int(p / max * 100)) + "% |" +

          '\33[107m' +
          " " * int((p / max) * 100 * barsize) +
          '\33[0m' +
          " " * int((100 - ((p / max) * 100)) * barsize) +

          "|" + str(int(p/1024 / 1024)) + " MB" + "/" + str(int(max/1024 / 1024)) + " MB" + " " * 10, end=""
          )


def getStreamMetaData(html : str ) -> dict:
    keyindex = html.find(MetaDataEnum.TOPLEVEL)
    data = extractOBJ(html , keyindex )
    return json.loads( data )


def extractOBJ(row: str, keyindex: int ) -> str:

    data: str = ""
    scopeFound = 0
    stack = 0

    scope : int = 0


    if keyindex == -1:
        raise Exception("key not found")



    while keyindex < len(row):

        c = row[keyindex]
        keyindex += 1

        if scopeFound == 0: 
            if c == '{' or c == '[':
                scope = ord(c)
                scopeFound = 1

        if ord(c) == scope and scope :
            stack += 1

        if ord(c) == scope + 2 and scope :
            stack -= 1

        if scopeFound:
            data += c

        if stack == 0 and scopeFound:
            break

    return data


def getVideoAudioMetaData(objs) -> set:

    V = []
    A = []

    for i in objs:
        try:
            if "video/" in str(i['mimeType']):
                V.append(i)
            else:
                A.append(i)
        except Exception as e:
            print(e)

    return (V, A)




def downloadFile(vUrl: str, aUrl : str , title: str):
    path = "Download"

    WebService.getFile(vUrl, title, path, prograssbar)
    print()

def getCipherInitfunction(js : str):
    regx = re.compile(r'\b([\w]+)\s*=\s*function\s*\(\s*a\s*\)\s*\{\s*a\s*=\s*a.split\s*\(\s*""\s*\);')
    res = regx.search(js)
    
    return res.span()


def getCipherSubFunctions(initFun : str) -> dict:
    regx = re.compile(r'\b(\w+\.\w+)\(\s*a,\s*(\d+)\);')
    res = regx.findall(initFun)

    if not res:
        raise Exception("js decode function map failed")

    li = []

    try:
        for i in res:
            li.append(f"{i[0]}:{i[1]}")
        
        return li
    except Exception as e:
        raise Exception("maping failed")



def findBasesOfSubFunctions(calls : list) -> set:
    bases : list = []

    regx = re.compile(r'\b(\s*\w+)\.')
    
    for b in calls:
        res = regx.search(b)

        try:
            bases.append(res.group(1))
        except Exception as e:
            pass
    if not len(bases):
        raise Exception("bases can not find")

    
    return set(bases)


def getSubFunctionsBodyMap(js :str , bases : set) -> dict :

    def reverse(a : list, b=None):
        a.reverse()
        
    def splice(s ) :
        s = int(s)
        def f1(a : list , b : int):
            for i in range(0,b):
                a.pop(s)
        return f1
        
    def swap(i: int):

        def f2(a : list , n : int):
            temp = a[i]
            a[i] = a[n % len(a)]
            a[n % len(a)] = temp

        return f2


    

    fbmap : dict= {}

    for base in bases:
        regx = re.compile(r'var\s*{}\s*=\s*'.format(base))
        res = regx.search(js)
        try:
            fb = extractOBJ(js , res.span()[1]).replace("\n" , "")
            reg = r"\b(\w+)\s*:\s*function\s*\([\w,]+\)\s*\{(\s*[^\}]+)\}"
            s = re.sub(reg , r'"\1" : "\2"' , fb ).replace(" " , "").replace("\n" , "")
            fbmap[base] = json.loads(s)

            mf = fbmap[base]

            for i in mf:
                if "reverse" in mf[i]:
                    mf[i] = reverse
                elif "splice" in mf[i]:
                    reg = r"\b\w.splice\((\d),b\)"
                    res = re.search(reg , mf[i])
                    mf[i] = splice(res.group(1))
                else:
                    res = re.search(r'\w\s*\[\s*(\d)\];' , mf[i])
                    mf[i] = swap(int(res.group(1)))        


        except Exception as e:
            raise Exception("functions body extraction failed :" + str(e))
    
    return fbmap
        











