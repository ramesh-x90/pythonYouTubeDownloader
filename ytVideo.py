from typing import Callable
from fileQualityEnum import AUDIOQUALITY, VIDEOQUALITY
from metaDataEnum import MetaDataEnum
from ytFunctions import downloadFile , extractOBJ, findBasesOfSubFunctions , getCipherInitfunction, getCipherSubFunctions, getStreamMetaData, getSubFunctionsBodyMap, getVideoAudioMetaData
from WebService import WebService
from urllib.parse import unquote , quote
import re


class ytVideo:

    def __init__(   self , 
                    url : str , 
                    vQ  : str = VIDEOQUALITY.MEDIUM , 
                    aQ  : str = AUDIOQUALITY.MEDIUM    
                ) -> None:

        if "low" in vQ.lower():
            self.vQ = VIDEOQUALITY.LOW
        elif "medium" in vQ.lower():
            self.vQ = VIDEOQUALITY.MEDIUM
        elif "high" in vQ.lower():
            self.vQ = VIDEOQUALITY.HIGH
        else:
            self.vQ = VIDEOQUALITY.LOW


        if "low" in aQ.lower():
            self.aQ = AUDIOQUALITY.LOW
        elif "medium" in aQ.lower():
            self.aQ = AUDIOQUALITY.MEDIUM
        elif "high" in aQ.lower():
            self.aQ = AUDIOQUALITY.MEDIUM
        else:
            self.aQ = AUDIOQUALITY.LOW

        self.hosturl = "https://www.youtube.com"

        self.url  : str = url
        self.html : str = WebService.getHtml(url)
        self.streamMetaData = getStreamMetaData(self.html)

        self.title : str =   self.getVideoTitle()


        self._videoStreams_MetaData , self._audioStreams_MetaData  = getVideoAudioMetaData(self.streamMetaData[MetaDataEnum.STREAMDATA][MetaDataEnum.FORMATS])

        self._videoStreamData : dict = None
        self._audioStreamData : dict = None

        self._js    : str = None
        self._jsUrl : str = None 

        self._cipher :dict = {}

        try:
            self._videoStreamData : dict = self.getVideoData()
            self._audioStreamData : dict = self.getAudioData()
        except Exception as e:
            raise Exception("can not create ytVideo instance :" + e)

        if not self._videoStreamData.get("url") or not self._audioStreamData.get("url"):


            try:
                self._jsUrl = self.getJsUrl()
            except Exception as e:
                raise YtVideoException.JsUrlNotFound()
            
            self._js = WebService.getJs(self._jsUrl)

            print(self._jsUrl)

            try:
                dcS , v21 = getCipherInitfunction(self._js)
                self._cipher['dcipherFuncBody'] = extractOBJ(self._js , dcS)
                print(self._cipher['dcipherFuncBody'])

                self._cipher['dcipherFuncBody']  = getCipherSubFunctions(self._cipher['dcipherFuncBody'])
                print(self._cipher['dcipherFuncBody'] )

                baseVarName : set = findBasesOfSubFunctions(self._cipher['dcipherFuncBody'] )
                print(baseVarName)

                self._cipher['functionsMap'] = getSubFunctionsBodyMap(self._js , baseVarName)



                
            except Exception as e:
                raise YtVideoException.JsDecryptFunctionNotFound()


            try:
                self._videoStreamData["url"] = extractCipherLink(
                    self._videoStreamData.get("signatureCipher"),
                    self.decryptUrl
                    )

                self._audioStreamData["url"] = extractCipherLink(
                    self._audioStreamData.get("signatureCipher"),
                    self.decryptUrl
                    )

                print(self._videoStreamData['url'])
                print(self._audioStreamData['url'])

            except Exception as e:

                print(e)
        
    def decryptUrl(self ,s : str):
        s = unquote(s)
        s = [c for c in s]
        for i in self._cipher['dcipherFuncBody']:
            res = re.search(r'(\w+)\.(\w+):(\d+)' , i)
            self._cipher['functionsMap'][res.group(1)][res.group(2)]( s , int(res.group(3)))
        s = "".join(s)
        return quote(s)



    def getJsUrl(self):

        if self._jsUrl:
            return self._jsUrl
        

        regex  = r'"([/\w+\.]+\/base.js)\b"'
        reg = re.compile(regex)

        res = reg.search(self.html)

        return f"{self.hosturl}{res.group(1)}"

    def downloadVideo(self):
        downloadFile( self._videoStreamData["url"] ,self._audioStreamData["url"], self.title)
        pass


    def getVideoTitle(self ) -> str:
        try:
            title: str = self.streamMetaData[MetaDataEnum.VIDEODETAILS][MetaDataEnum.VIDEOTITEL]

            title = title.replace("|", "").replace(
                "-", "").replace("[", "").replace("]", "")

            return title

        except Exception as e:
            return "title-unkown"

    
    def getVideoData(self) -> dict:

        for i in self._videoStreams_MetaData:
            try:
                if self.vQ in i['qualityLabel']:
                    return i 
            except Exception as e:
                raise Exception("failed to extract choosen video data")



    def getAudioData(self) -> dict:

        for i in self._audioStreams_MetaData:
            try:
                if self.aQ in i['audioQuality']:
                    return i
            except Exception as e:
                raise Exception("failed to extract choosen audio data")





class YtVideoException:
    base = "ytVideo Error"
    class JsUrlNotFound(Exception):
        def __init__(self) -> None:
            super().__init__(YtVideoException.base + ":JsUrlNotFound")
    class JsDecryptFunctionNotFound(Exception):
            def __init__(self) -> None:
                super().__init__(YtVideoException.base + ":JsDecryptFunctionNotFound")
    class signatureCipherNotFound(Exception):
            def __init__(self) -> None:
                super().__init__(YtVideoException.base + ":signatureCipherNotFound")

def extractCipherLink(signatureCipher : str , func : Callable[[ytVideo , str] , str]) -> dict:
    s = None
    url = None
    tag = None

    for i in signatureCipher.split("&"):
        if re.search(r'^s=' , i):
            s = "".join(i.split("=")[1:])
        elif re.search(r'^sp=' , i):
            tag = "".join(i.split("=")[1:])
        elif re.search(r'^url=' , i):
            url = unquote("".join(i.split("=")[1:])) 
    

    return f"{url}&{tag}={func(s)}"

# class test
if __name__ == "__main__":
    ytVideo("https://youtu.be/hq_AV304EM8" , vQ="low" , aQ="low")
    ytVideo("https://youtu.be/pl5WHx8QCVk" , vQ="high" , aQ="high")
    ytVideo("https://youtu.be/pOoR5KFDD_w" , vQ="high" , aQ="high")
