from io import TextIOWrapper
import os
from os import write
from typing import Callable, Iterable
import requests as rq
from requests.sessions import Session


class WebService:

    s: Session = rq.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
    }

    s.headers.update(headers)

    @staticmethod
    def getHtml(url: str) -> str:

        data = WebService.s.get(url)

        if data.status_code != 200:
            raise Exception("invalid url")
        
        f = open("index.html" , "wb")
        d : str = data.text
        d  = d.replace(r"\u0026", "&")

        f.write(d.encode())
        f.close()

        return d

    @staticmethod
    def getFile(url, title: str, path: str, func: Callable[[int, int], None] = None):

        data = WebService.s.get(url, stream=True)
        header = data.headers

        if data.status_code != 200:
            raise Exception("invalid url")

        try:
            if header['Accept-Ranges'] != "bytes":
                raise Exception("invalid url")

            filetype = header['Content-Type'].split(r"/")[1]
            c_len = int(header['Content-Length'])

            print(filetype)
            print(c_len)

            try:
                os.makedirs(path)
            except Exception as e:
                pass

            fileName = f"{path}/{title}.{filetype}"

            if os.path.exists(fileName):
                # os.remove(fileName)
                print("file overriding...")

            f: TextIOWrapper = open(fileName, "wb")

            chunks = 0
            chunkSize = 1024*1

            for chunk in data.iter_content(chunk_size=chunkSize):
                if func != None:
                    func(chunks, c_len)
                f.write(chunk)
                chunks += chunkSize

            f.close()

        except Exception as e:
            print(e.__str__())
            raise Exception(e)

        data.close()

        pass

    @classmethod
    def getJs(cls , url: str) -> str:
        f = open("base.js" , "w")
        data = cls.getHtml(url)
        f.write(data)
        f.close()
        return data