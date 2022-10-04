from typing import Iterable
from ytVideo import ytVideo
from WebService import WebService
from metaDataEnum import MetaDataEnum
from fileQualityEnum import AUDIOQUALITY, VIDEOQUALITY
import os
import json
from bs4 import BeautifulSoup 


def main():

    fileName = "Meta-data.json"
    fileName2 = "index.html"
    # fileName = "index.html"
    Vquality = VIDEOQUALITY.LOW
    Aquality = AUDIOQUALITY.LOW

    # if os.path.exists(fileName):
    #     os.remove(fileName)

    f = open(fileName, "w")
    f2 = open(fileName2, "wb")

    try:

        url = f"https://youtu.be/hq_AV304EM8"

        try:


            # bs = BeautifulSoup(html , "html5lib")
            # scripts = bs.find_all("script")
            # for s  in scripts:
            #     # f2.write(s.encode())
            #     print(str(s).find("ytInitialPlayerResponse"))
            ytVideo("https://youtu.be/hq_AV304EM8" , vQ="low" , aQ="low")



        except Exception as identifier:
            print(identifier)
            return 0

    except Exception as e:
        print(e)

    f.close()


if __name__ == "__main__":
    main()
