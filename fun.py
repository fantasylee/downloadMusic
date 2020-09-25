from PyQt5 import QtCore, QtGui, QtWidgets
from selenium import webdriver
import time,os,configparser,requests,json

import sys, os, time
import configparser


class Config(object):
    def __init__(self, path):
        self.path = path
        self.cf = configparser.ConfigParser()
        self.cf.read(self.path)

    def get(self, field, key):
        try:
            result = self.cf.get(field, key)
        except:
            result = ""
        return result

    def set(self, filed, key, value):
        try:
            self.cf.set(filed, key, value)
            with open(self.path, 'w') as f:
                self.cf.write(f)
        except:
            pass
        return True
    def startConfig(self):
        config = Config(self.path)
        iniPath=config.get("downFilePath", "path")
        value=os.path.isdir(iniPath)
        if value :
            return iniPath
        else:
            cwdpath=os.getcwd()
            config.set("downFilePath", "path",cwdpath)
            return cwdpath

class SetJson(object):
    def __init__(self,path):
        self.path = path


def getResult(dr):
    dr.switch_to.frame("g_iframe")
    searchResultPk = dr.find_element_by_class_name("srchsongst").find_elements_by_xpath("./div")
    resultPack = []
    for result in searchResultPk:
        songInfo = result.find_elements_by_xpath("./div")
        songNameInfo = (songInfo)[1]  # 每个div下面有五个a标签，第2,4,5分别为歌曲名，作者名，专辑名(有部分歌曲没有songAlbumUrl，报错)
        songName, songNameUrl = songNameInfo.text, songNameInfo.find_element_by_tag_name("a").get_attribute("href")
        songArtistInfo = songInfo[3]
        songArtistName_source = songArtistInfo.text
        songArtistName = songArtistName_source.replace("/", "+")
        songAlbumInfo = songInfo[4]
        songAlbumName = songAlbumInfo.text
        songTime = result.find_elements_by_xpath("./div")[-1].text
        songId = songNameUrl.split("id=")[-1]  # 分割url字符串，获取songID
        resultPack.append((songName, songArtistName, songAlbumName, songTime, songId))
    [Config("config.ini").set("songId", str(i), resultPack[i][-1]) for i in
     range(len(resultPack))]  # 将获取的songId加到config.ini文件中
    [Config("config.ini").set("songName", str(i), resultPack[i][1] + "-" + resultPack[i][0]) for i in
     range(len(resultPack))]  # 将获取的songName加到config.ini文件中
    return resultPack
def getDicResult(dr):
    dr.switch_to.frame("g_iframe")
    searchResultPk = dr.find_element_by_class_name("srchsongst").find_elements_by_xpath("./div")
    resultPack = []
    for result in searchResultPk:
        songInfoDic={}
        songInfo = result.find_elements_by_xpath("./div")
        songNameInfo = (songInfo)[1]  # 每个div下面有五个a标签，第2,4,5分别为歌曲名，作者名，专辑名(有部分歌曲没有songAlbumUrl，报错)
        songName, songNameUrl = songNameInfo.text, songNameInfo.find_element_by_tag_name("a").get_attribute("href")
        songArtistInfo = songInfo[3]
        songArtistName_source = songArtistInfo.text
        songArtistName = songArtistName_source.replace("/", "+")
        songAlbumInfo = songInfo[4]
        songAlbumName = songAlbumInfo.text
        songTime = result.find_elements_by_xpath("./div")[-1].text
        songId = songNameUrl.split("id=")[-1]  # 分割url字符串，获取songID
        songInfoDic["songName"] = songName
        songInfoDic["songNameUrl"] = songNameUrl
        songInfoDic["songArtistName"] = songArtistName
        songInfoDic["songAlbumName"] = songAlbumName
        songInfoDic["songTime"] = songTime
        songInfoDic["songId"] = songId
        songInfoDic["songName"] = songName
        resultPack.append(songInfoDic)
    with open("searchResult.json","w",encoding="utf-8") as file:
        json.dump(resultPack,file,ensure_ascii=False)
    # return resultPack

def search_163music(dr,word):#获取网易云搜索列表结果
    search_url = "https://music.163.com/#/search/m/?s={word}".format(word=word)
    dr.get(search_url)
    time.sleep(0.5)
    result=getResult(dr)
    return result
def checkFile(path,resourceFileName):
    for root, dirs, files in os.walk(path):
        while resourceFileName+".mp3" in files:
            resourceFileName += "_1"
    return resourceFileName


def songDownload(songName,songId,path):#下载音乐
    songDownLink="http://music.163.com/song/media/outer/url?id={muId}".format(muId=songId)
    header={
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}
    songNameF=checkFile(path,songName)
    if songName == songNameF:
        isRepeat = False
    else:
        isRepeat = True
    print("start to download "+songName)
    res=requests.get(songDownLink,headers=header).content
    with open(path+"/"+songNameF+".download","wb") as f:
        try:
            f.write(res)
            isSuccess = True
        except:
            isSuccess =  False
    if isSuccess:
        os.rename(path+"/"+songNameF+".download",path+"/"+songNameF+".mp3")
    return isSuccess,isRepeat,songNameF



if __name__ == '__main__':
    # search_163music("周杰伦"
    # songDownload("红色高跟鞋+蔡健雅","208902","D:/mine/MusicDownload/Demo")
    pass
    dr = webdriver.Chrome()
    search_url = "https://music.163.com/#/search/m/?s={word}".format(word="五月天")
    dr.get(search_url)
    time.sleep(0.5)
    result=getDicResult(dr)