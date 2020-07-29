import lxml.etree as et
from urllib.parse import unquote
import glob
import os

m3uPath = "C:\\Users\\yjy\\Music\\iTunes\\iTunes Media\\Music"
root = et.parse("C:\\Users\\yjy\\Music\\iTunes\\iTunes Music Library.xml").getroot()
dictRoot = root.find("dict")

ShortSplitLine = "- - - - - - - - - - - - - -"
LongSplitLine = "\n===========================\n"

arrayPlaylists = None
dictTracks = None

keysRoot = dictRoot.findall("key")
for key in keysRoot:
    if key.text == "Playlists":
        arrayPlaylists = key.getnext()
    elif key.text == "Tracks":
        dictTracks = key.getnext()

tracks = {}

print(LongSplitLine)

print("开始解析歌曲")
keyDictTracks = dictTracks.findall("key")
for key in keyDictTracks:
    #一个key后面是一个dict
    #一个dict中有很多key，一个key后面是一个string，对应track的一项信息
    id = key.text
    keyInfos = key.getnext().findall("key")
    for key in keyInfos:
        if key.text == "Location":
            tmpString = key.getnext().text
            tracks[id] = unquote("\\".join(tmpString.split('/')[-3:]), encoding="utf-8")
            #print(tracks[id])
            break
print(ShortSplitLine)
print("歌曲解析完毕")

print(LongSplitLine)

print("删除 "+m3uPath+" 下的旧m3u文件")
print(ShortSplitLine)
for f in glob.glob(os.path.join(m3uPath, "*.m3u")):
    print(f)
    os.remove(f)
print(ShortSplitLine)
print("删除完毕")

print(LongSplitLine)

#生成一个forgotten列表
willGenForgotten = True
if willGenForgotten:
    ForgottenString = "__forgotten__"
    existInItunes = False
    hasNewForgotten = False
    forgotten = dict.fromkeys(tracks.keys(), 1)

#检查是否有歌曲存在于多个播放列表
checkDup = True
if checkDup:
    playlistOfTracks = {key:list([]) for key in tracks.keys()}
    dupTracks = {}

def makeM3u(prefix,playlistName,playlist):
    # 生成m3u
    stringM3u = ("\n"+prefix).join(["#EXTM3U"]+[tracks[id] for id in playlist])
    #print(stringM3u + "\n")

    f = open(m3uPath + "\\" + playlistName + ".m3u", "w", encoding="utf-8")
    f.write(stringM3u)
    f.close()

print("开始解析播放列表")
print(ShortSplitLine)
dictArrayPlaylists = arrayPlaylists.findall("dict")
for dict in dictArrayPlaylists:
    playlistName = ""
    playlist = []
    for key in dict.findall("key"):
        if key.text == "Name":
            playlistName = key.getnext().text
            break
    discardedList = ['资料库','已下载','音乐','影片','电视节目','播客','有声书']
    if willGenForgotten:
        discardedList += [ForgottenString]
    if playlistName in discardedList:
        if playlistName == ForgottenString:
            existInItunes = True
        continue
    #清理playlistName，使其可用于命名文件
    while True:
        if playlistName[0] != ' ':
            break
        playlistName = playlistName[1:]
    for c in ['?','*',':','\"','<','>','\\','/','|']:
        playlistName = playlistName.replace(c,'_')
    array = dict.find("array")
    if array == None:
        continue

    print(playlistName)
    dictTracks = array.findall("dict")
    for dict in dictTracks:
        id = dict.find("integer").text
        playlist.append(id)
        if willGenForgotten:
            forgotten[id] = False
        if checkDup:
            if len(playlistOfTracks[id]) > 0:
                dupTracks[id]=1
            playlistOfTracks[id].append(playlistName)
    makeM3u('\\',playlistName, playlist)

if willGenForgotten:
    playlistName = ForgottenString
    playlist = []
    for id in forgotten.keys():
        if forgotten[id] == True:
            playlist.append(id)
    if len(playlist) > 0:
        hasNewForgotten = True
        print(playlistName+"\n")
        makeM3u(m3uPath+'\\', playlistName, playlist)

    print(ShortSplitLine)
    if not hasNewForgotten:
        print("没有forgotten歌曲！")
        if existInItunes:
            print("请删除iTunes中的"+ForgottenString+"列表")
    else:
        print("\n已生成新的"+ForgottenString+".m3u")
        if existInItunes:
            print("请删除iTunes中的"+ForgottenString+"列表，然后导入新m3u")
        else:
            print("请导入新m3u")

if checkDup:
    print(ShortSplitLine)
    if len(dupTracks.keys()) > 0:
        print("在播放列表中重复的歌曲：")
        for id in dupTracks.keys():
            print(tracks[id])
            print(playlistOfTracks[id])
    else:
        print("没有在播放列表中重复的歌曲！")
print(ShortSplitLine)
print("m3u文件已生成到 "+m3uPath)
print(ShortSplitLine)
print("解析播放列表完毕")
print(LongSplitLine)
print("程序运行结束")
print(LongSplitLine)