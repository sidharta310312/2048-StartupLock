#2048 written in Python, made by Sidharta310312 on GitHub
#Took me a few weeks to make (it took that long because I'm busy with school and I was studying for my finals)
#Don't forget to check README.md on my repo!

"""WHY THIS PROJECT IS INTERESTING?"""
# 1. Data-saving system! Yes, you can save and load 2048 games you've had before (and there's no limit on saving games! Except your hard disk space of course.)
# 2. Smooth GUI effects, glide and transition smoothly (worked pretty hard on that)
# 3. Startup Lock Mode : You can lock computers upon startup using this game, more description available in README.md (Only available in Windows, which is unfortunate for MacOS, Linux, and other users)
# 4. Board Resizing : Most 2048 games you see have a fixed 4x4 board size, but in this game, you can set the width and height values from 2 to 10 tiles!
#    (2x2, 4x4, 10x10, 7x8, 6x7, and much more! There are 81 possible size combinations)


#PS. Due to Startup Lock Mode existing, you can install this game into your friends' computer and auto-lock their PCs everytime it's turned on

import pygame #main GUI library for this project
import sys
import random
import time
import requests
from pathlib import Path
import os
import getpass, socket
import string
import json
from datetime import datetime
import math
import webbrowser
import tkinter as tk #the tkinter library only used for getting the monitor size instead of GUI purposes lmao
import winreg

print("system arguments found : " , sys.argv)
print(str(datetime.now()))

saveFile_drive = "D"

if "--startup" in sys.argv:
    time.sleep(5) #Delay for Startup Lock mode (give Windows some time to prepare all files and systems)

pygame.init()

pygame.display.set_caption("2048")

screensize = (800,800)
screen = pygame.display.set_mode(screensize)
centerPos = (screensize[0]//2, screensize[1]//2)

assets_directory = os.path.join(os.getenv("APPDATA"), "2048assets")
os.makedirs(assets_directory, exist_ok=True)

if os.path.isdir(f"{saveFile_drive}:/"):
    os.makedirs(f"{saveFile_drive}:/2048userdata", exist_ok=True)
else:
    print("Save drive not found, disabling datasaving systems")

#init colors
red = (255, 94, 58)
darkRed = (139, 0, 0)

green = (0,255,0)
darkGreen = (0, 100, 0)

lightBlue = (203, 230, 253)
darkBlue = (0, 0, 255)
blue = (0, 191, 255)
white = (255,255,255)
black = (0,0,0)
yellow = (230, 203, 102)

darkYellow = (166, 147, 109)

taupeColor = (153, 142, 131)
darkTaupe = (85, 70, 58)

bgColor = (249, 246, 239)

#init functions

def FormatTime(n):
    minutes, seconds = divmod(n, 60)
    hour, minutes = divmod(minutes, 60)

    return f"{int(hour):02d}:{int(minutes):02d}:{int(seconds):02d}"

def FetchImage(fileName, source):
    WebResponse = requests.get(source)
    if WebResponse.status_code == 200:
        with open(Path(assets_directory + "/" + fileName), "wb") as file:
            file.write(WebResponse.content)
        return True
    return False

def UnpackSublists(thelist):
    newList = []
    for sublist in thelist:
        for item in sublist:
            newList.append(item)

    return newList

def MakeText(text,size,color,pos,thick):
    newText = pygame.font.SysFont('Consolas', size, bold=thick).render(text, True, color)
    newText_rect = newText.get_rect()
    newText_rect.center = pos
    screen.blit(newText,newText_rect)
    return newText_rect

def RenderBoard(boardData):
    margin = 80/len(boardData)
    boardRect = pygame.Rect(0,0,500,500)
    boardRect.center = centerPos[0], centerPos[1] - 50

    pygame.draw.rect(screen, darkTaupe, boardRect)
    tileSize = (boardRect.size[0] / boardSize[0] - margin, boardRect.size[1] / boardSize[1] - margin)
    
    tilePos = []

    for Y_pos, row in enumerate(boardData):
        for X_pos, item in enumerate(row):
            newTile = pygame.Rect(boardRect.topleft, tileSize)
            newTile.topleft = newTile.topleft[0] + (margin * X_pos) + (X_pos * tileSize[0]) + (margin/2), newTile.topleft[1] + (margin * Y_pos) + (Y_pos * tileSize[1]) + (margin/2)
            
            
            if item != 0:
                #print(item)
                blockColors = ((242, 236, 222), #Logarithmic value = 1 (Refers to 2)
                               (238, 230, 203), #Log value = 2 (Refers to 4)
                               (249, 176, 107), #Log value = 3 (8)
                               (255, 152, 96), #Log value = 4 (16)
                               (251, 129, 101), #Log value = 5 (32)
                               (246, 94, 59), #Log value = 6 (64)
                               (237, 207, 114) #Log value = 7 (128)
                               )
                if item <= len(blockColors):
                    pygame.draw.rect(screen, blockColors[item-1], newTile)
                else:
                    pygame.draw.rect(screen, black, newTile)
                
                MakeText(str(1 << item), int(200/boardSize[0]), white, newTile.center, False)
                
            else:
                pygame.draw.rect(screen, taupeColor, newTile)
            #pygame.display.flip()
            if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
                MakeText(f"X: {X_pos}, Y: {Y_pos}", 10, red, (newTile.center[0], newTile.center[1] + 20), False)
    
    return boardRect.topleft, tileSize #returns board position AND size of each tile

def AddRandomNumber(boardData):
    newBoard = boardData
    empty_Indexes = []

    for row_index in range(len(boardData)):
        column = boardData[row_index]
        for column_index, item in enumerate(column):
            if item == 0:
                empty_Indexes.append([row_index, column_index])

    selectedIndex = empty_Indexes[random.randint(0, len(empty_Indexes)-1)]
    newBoard[selectedIndex[0]][selectedIndex[1]] = 1
    #index 0 = row (Y)
    #index 1 = column (X)
    
    return newBoard, (selectedIndex[1], selectedIndex[0]) #New board_data after random number added, Random number position on board

def CombineNumbers(Data, Direction): #0 to LEFT
    originalLength = len(Data)
    Data = [x for x in Data if x > 0]
    skip = False
    modifiedData = [0]*len(Data)
    
    for index in (range(0, len(Data)), range(len(Data)-1, -1, -1))[Direction]:
        if index != (len(Data)-1, 0)[Direction]:
            if skip:
                skip = True
                continue

            item = Data[index]
            nextItem = Data[index + (1,-1)[Direction]]
            if item == nextItem:
                Data[index + (1,-1)[Direction]] = 0
                Data[index] = item + 1
                #Data[index], Data[index + (-1,1)[Direction]] = item + 1, 0
        
    Data = [x for x in Data if x > 0]
    Data = (Data + [0]*(originalLength - len(Data)), [0]*(originalLength - len(Data)) + Data)[Direction]
    
    return Data

def GetUserData():
    if os.path.isdir(f"{saveFile_drive}:/"):
        return [f for f in os.listdir(f"{saveFile_drive}:/2048userdata/") if os.path.isfile(f"{saveFile_drive}:/2048userdata/{f}") and ".json" in f]
    return []

def ReadJSON(filename):
    try:
        with open(f"{saveFile_drive}:/2048userdata/" + filename, "r") as contents:
            return (json.load(contents), filename)
    except:
        return "NOTFOUND"

def SaveData(filename, filedata):
    saving_path = os.path.join(Path(f"{saveFile_drive}:/2048userdata/"), f"{filename}.json")
    print("SAVING DATA TO " + saving_path)
    with open(Path(saving_path), "w") as file:
        json.dump(filedata, file)

def activate_StartupLock(timer, score):
    python_dir = os.path.join(os.path.dirname(sys.executable), "pythonw.exe") #REMINDER TO SELF : pythonw.exe is basically python.exe but without terminal windows showing up
    script_dir = os.path.abspath(__file__)
    command = f'"{python_dir}" "{script_dir}" --startup {timer} {score}'

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
    )

    winreg.SetValueEx(key, "2048_StartupLock", 0, winreg.REG_SZ, command)
    winreg.CloseKey(key)
    print("2048 Startup Mode established!")

def delete_StartupLock():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "2048_StartupLock")
        winreg.CloseKey(key)
        return "DELETED"
    except FileNotFoundError:
        return "NOTFOUND"
    except PermissionError:
        return "PERMISSIONERROR"

def check_winreg():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ  # Read permission only
        )

        i = 0
        keepchecking = True
        while keepchecking:
            try:
                if winreg.EnumValue(key, i)[0] == "2048_StartupLock":
                    keepchecking = False
                    return True
                i += 1
            except OSError: #if no more windows registries to check
                keepchecking = False
                return False
    except FileNotFoundError:
        return False
    except PermissionError:
        return False

#MAKE LOADING SCREEN
MakeText("Loading content...", 40, white, centerPos, True)
MakeText("Initiating some variables", 20, white, (centerPos[0], centerPos[1] + 50), False)
pygame.display.flip()


#init variables
TimerVariable = 0
FPS_Control = pygame.time.Clock()
gameData = []
page = "loadin"
timeStarted = 0
gameover = False
show_gameoverTip = 0
creditText_xpos = 200

allJSON_files = GetUserData()
print("JSON save files : " , allJSON_files)
selected_userData = {}
userData_page: int = 0

play_btn_size: int = 128


icons_transitionPos = [-100]*4
icons_transitionIndex = 0
icon_flashbang = [255] * 4

page_flashbangValue = 255
newblock_flashbangValue = {"Opacity":0,
                           "Position":(0,0)}

warningText_Ypos = 0
warningText_string = ""
SLdelete_warn = ["", 0] #will be used for startup lock mode settings
SaveName_string = ""
SaveAlert_time = 0
twoStep_SNverification = False
show_eastereggInfo = False

#init rects & buttonz
cursor = pygame.Rect(0,0,10,10)
startBtn = pygame.Rect(0,0,300,100)
loadBtn = pygame.Rect(0,0,300,50)
iconRects = [pygame.Rect(0,0,100,100), pygame.Rect(0,0,100,100), pygame.Rect(0,0,100,100), pygame.Rect(0,0,100,100)]
newGameBtn = pygame.Rect(0,0,10,10)
warnBtnChoices = [pygame.Rect(0,0,300,60), pygame.Rect(0,0,300,60)] #first = Yes, second = No
creditTextRect = pygame.Rect(0,0,0,0)

loadGame_btns = {"PLAY":pygame.Rect(0,0,0,0), "DELETE":pygame.Rect(0,0,0,0)}
loadGame_pagebuttons = {"PREVIOUS":pygame.Rect(0,0,150,50), "NEXT":pygame.Rect(0,0,150,50)}
#boardRect = pygame.rect(0,0,300,100)

#init tables
targetSequence = ["up", "up", "down", "down", "left", "right", "left", "right", "b", "a", "return"]
incrementBtn = {"plus":(pygame.Rect(0,0,75,75), pygame.Rect(0,0,75,75)),
                "minus":(pygame.Rect(0,0,75,75), pygame.Rect(0,0,75,75))}
boardSize = [4,4]
numOccup = []
currentScore = 0
movesMade = 0
KeySequenceIndex = 0


MakeText("Loading content...", 40, white, centerPos, True)
MakeText("Getting images...", 20, white, (centerPos[0], centerPos[1] + 50), False)
pygame.display.flip()

#get assets from le internet
imageSources = {"LEFT_ARROW":"https://i.postimg.cc/7GpDvJxb/LEFT-ARROW.png",
                "DOWN_ARROW":"https://i.postimg.cc/YGJkcLp4/DOWN-ARROW.png",
                "RIGHT_ARROW":"https://i.postimg.cc/CBWYynFx/RIGHT-ARROW.png",
                "UP_ARROW":"https://i.postimg.cc/TLZG85Rp/UP-ARROW.png",
                "ICON":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzFd-U62JmJydaMEuacfY4ye5Uij6CU7b_mg&s",
                "GTAU BRO":"https://static.wikia.nocookie.net/backrooms/images/0/05/Thebackrooms.jpg/revision/latest?cb=20230105020740",
                "HOMEICON":"https://i.postimg.cc/pLb5JnQw/Home-Icon.png",
                "DANGERSIGN":"https://i.postimg.cc/Xq0GC2R0/canva-warning-safety-sign-MACb0War-Tkg.png",
                "SKILLISSUE":"https://i.postimg.cc/9QrfcTKT/whyisthisimageinjpg.jpg",
                "PLAYBTN":"https://i.postimg.cc/MKdpr1ND/play-button-icon-png-10.png"}

imageCropSize = {"DOWN_ARROW":(30,30),
                 "UP_ARROW":(30,30),
                 "LEFT_ARROW":(30,30),
                 "RIGHT_ARROW":(30,30),
                 "ICON":(64,64),
                 "GTAU BRO":screensize,
                 "HOMEICON":(64,64),
                 "DANGERSIGN":(150,150),
                 "SKILLISSUE":(128,128),
                 "PLAYBTN":(64,64)}

imageSurfaces = {}
images_loaded = 0

for imgName in list(imageSources): #Download game assets
    screen.fill(black)
    image_path = Path(os.path.join(assets_directory, imgName))
    
    MakeText("Loading content...", 40, white, centerPos, True)
    MakeText(f"Getting images... ({images_loaded}/{len(imageSources)})", 20, white, (centerPos[0], centerPos[1] + 50), False)

    MakeText(f"If the program crashes mid-way loading, just close and reopen and the loading will continue", 15, yellow, (centerPos[0], screensize[1] - 50), False)

    print(f"Loading asset no. {images_loaded} : {imgName}")
    pygame.display.flip()

    #print(type(os.path.join(assets_directory, imgName)))

    if not image_path.is_file():
        FetchImage(imgName, imageSources[imgName])
    

    images_loaded += 1
    imageSurfaces[imgName] = pygame.transform.smoothscale(pygame.image.load(image_path).convert_alpha(), imageCropSize[imgName])


HomeIcon_rect = imageSurfaces["HOMEICON"].get_rect()

startuplock_Settings = {"SCORE":8, "TIMER":0}
startuplock_UIpos = [centerPos[1] * 0.8, centerPos[1] * 1.2, centerPos[1] * 1.6]

ArrowKeyPressed = ""



if images_loaded == len(imageSources):
    page = "start"

pygame.display.set_icon(imageSurfaces["ICON"])

gameloop = True

#NORMAL GAMEPLAY
while gameloop:
    ArrowKeyPressed = ""
    FPS_Control.tick(60)
    screen.fill(bgColor if not "easteregg" in page
                 else black)
    cursor.center = pygame.mouse.get_pos()

    if __name__ == "__main__" and len(sys.argv) > 1:
        gameloop = not "--startup" in sys.argv

    if images_loaded == len(imageSurfaces): #Check input and output
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                screen.blit(imageSurfaces["GTAU BRO"], (0,0))
                pygame.display.set_icon(imageSurfaces["GTAU BRO"])
                pygame.display.set_caption(f"L̴̮̬̼̩͂̆̓̊͝O̴͓̝͆̏̈́O̴̮͑̈́̄͜͜K̵͕̯̩̞̗͊ ̶̯̆̈́̆B̴̨̟͔͋̉͠Ë̸̝͕̺̺͉́͊̄͘͝H̷̯͒̋͋͋͘Ḯ̵̳̲̐͘N̸͎̯̂͝D̷͖̆ ̴̬̫̒̔̇͐̌Y̸͙͖͆͜Ỏ̷̖̱͐̾͝Ü̷͇̙̦͎̉̐̿͋͜     {getpass.getuser()}")
                MakeText(str(local_ip),60, red, centerPos, True)
                pygame.display.flip()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if page == "start" and startBtn.colliderect(cursor):
                    page = "newGame" if numOccup == [] else "gameTime"
                    page_flashbangValue = 255
                    if numOccup != [] and not gameover:
                        timeStarted = time.time()
                    #transition = True
                elif page == "start" and newGameBtn.colliderect(cursor) and numOccup != []:
                    warningText_string = ""
                    if not gameover:
                        page_flashbangValue = 255
                        warningText_Ypos = screensize[1]
                        page = "warn"
                    else:
                        page_flashbangValue = 255
                        numOccup = []
                        boardSize = [4,4]
                        currentScore, movesMade = (0,0)
                        TimerVariable, timeStarted = (0,0)
                        gameover = False
                        warningText_Ypos = screensize[1]
                        warningText_string = ""
                        page = "newGame"

                elif page == "newGame":
                    if startBtn.colliderect(cursor):
                        numOccup = []
                        for row in range(boardSize[1]):
                            numOccup.append([0]*boardSize[0])
                        
                        numOccup = AddRandomNumber(numOccup)[0]

                        #numOccup[0] = [1]*4 + [0]*(len(numOccup[0])-4)

                        print(numOccup)
                        page_flashbangValue = 255        
                        page = "gameTransition"
                    for btnType in incrementBtn:
                        for index, btn in enumerate(incrementBtn[btnType]):
                            if btn.colliderect(cursor):
                                condits = {"plus":boardSize[index] < 10, "minus":boardSize[index] > 2}

                                if condits[btnType]:
                                    boardSize[index] += {"plus":1, "minus":-1}[btnType]

                elif page == "gameTime":
                    if cursor.colliderect(HomeIcon_rect):
                        if not gameover:
                            TimerVariable += time.time() - timeStarted
                        
                        icons_transitionPos = [-100]*4
                        icons_transitionIndex = 0
                        icon_flashbang = [255] * 4
                        creditText_xpos = 200

                        #page_flashbangValue = 255
                        startBtn = pygame.Rect(0,0,300,100)
                        page = "start"
                    elif cursor.colliderect(startBtn) and not gameover:
                        if Path(f"{saveFile_drive}:/").is_dir() and SaveName_string == "":
                            warningText_Ypos = 150
                            #startBtn.center = centerPos[0], screensize[1] - 100
                            SaveAlert_time = 0
                            twoStep_SNverification = False
                            page = "savingGame"
                        elif not Path(f"{saveFile_drive}:/").is_dir():
                            warningText_string = f"Drive {saveFile_drive} required to save games"
                            SaveAlert_time = time.time() + 3
                        elif SaveName_string != "":
                            data = {"boardSize":boardSize,
                                    "boardData":numOccup,
                                    "Timer" : TimerVariable + time.time() - timeStarted,
                                    "MovesMade":movesMade,
                                    "LastPlayed":str(datetime.now().date())}
                            saving_path = os.path.join(Path(f"{saveFile_drive}:/2048userdata/"), f"{SaveName_string}.json")
                            #print("SAVING DATA TO " + save_directory)
                            with open(Path(saving_path), "w") as file:
                                json.dump(data, file)
                            
                            warningText_string = f"Saved successfully as {SaveName_string}.json"
                            SaveAlert_time = time.time() + 3

                    elif cursor.colliderect(newGameBtn) and show_gameoverTip < time.time():
                        #page_flashbangValue = 255
                        numOccup = [[0]*boardSize[0]]*boardSize[1]
                        #boardSize = [4,4]
                        currentScore, movesMade = (0,0)
                        TimerVariable, timeStarted = (0,time.time())
                        gameover = False
                elif page == "warn":
                    for index, btn in enumerate(warnBtnChoices):
                        if btn.colliderect(cursor):
                            page = ["newGame", "start"][index]
                            if index == 0:
                                page_flashbangValue = 255
                                numOccup = []
                                boardSize = [4,4]
                                currentScore, movesMade = (0,0)
                                TimerVariable, timeStarted = (0,0)
                                gameover = False
                                warningText_Ypos = screensize[1]
                                warningText_string = ""
                    
                elif page == "savingGame" and startBtn.colliderect(cursor) and not twoStep_SNverification:
                    if len(SaveName_string) > 0 and SaveName_string + ".json" not in allJSON_files:
                        data = {"boardSize":boardSize,
                                "boardData":numOccup,
                                "Timer" : TimerVariable + time.time() - timeStarted,
                                "MovesMade":movesMade,
                                "LastPlayed":str(datetime.now().date())}
                        
                        SaveData(SaveName_string, data)
                        
                        page = "gameTime"
                        warningText_string = f"Saved successfully as {SaveName_string}.json"
                        SaveAlert_time = time.time() + 3
                    elif len(SaveName_string) <= 0:
                        SaveAlert_time = time.time() + 1
                    elif SaveName_string + ".json" in allJSON_files:
                        page_flashbangValue = 0
                        imageSurfaces["LEFT_ARROW"].set_alpha(180)
                        imageSurfaces["RIGHT_ARROW"].set_alpha(180)
                        twoStep_SNverification = True
                
                elif page == "savingGame" and HomeIcon_rect.colliderect(cursor):
                    icons_transitionPos = [-100]*4
                    icons_transitionIndex = 0
                    icon_flashbang = [255] * 4
                    creditText_xpos = 200

                    #page_flashbangValue = 255
                    startBtn = pygame.Rect(0,0,300,100)
                    page = "start"

                    if twoStep_SNverification:
                        twoStep_SNverification = False
                        SaveName_string = ""
                
                elif page == "start" and loadBtn.colliderect(cursor):
                    page_flashbangValue = 255
                    allJSON_files = GetUserData()
                    warningText_string = ""
                    page = "loadFile"

                elif page == "loadFile":
                    if cursor.colliderect(loadGame_btns["PLAY"]) and len(allJSON_files) > 0:
                        page = "gameTime"
                        page_flashbangValue = 255
                        boardSize, numOccup, timerVariable, movesMade = [selected_userData[0][key] for key in list(selected_userData[0])][0:4]
                        SaveAlert_time = time.time() + 3
                        SaveName_string = selected_userData[1][:-5]
                        warningText_string = "Successfully loaded " + selected_userData[1]
                        timeStarted = time.time()
                        selected_userData = {}
                    elif cursor.colliderect(loadGame_btns["PLAY"]) and len(allJSON_files) == 0:
                        page = "newGame"
                        page_flashbangValue = 255
                    elif cursor.colliderect(HomeIcon_rect):
                        icons_transitionPos = [-100]*4
                        icons_transitionIndex = 0
                        icon_flashbang = [255] * 4
                        creditText_xpos = 200
                        page = "start"
                    elif cursor.colliderect(loadGame_pagebuttons["PREVIOUS"]) and userData_page > 0:
                        userData_page -= 1
                    elif cursor.colliderect(loadGame_pagebuttons["NEXT"]) and userData_page < math.ceil(len(allJSON_files)/5) - 1:
                        userData_page += 1
                    elif cursor.colliderect(loadGame_btns["DELETE"]) and len(allJSON_files) > 0:
                        print(f"User requested to delete {selected_userData[1]}")
                        if warningText_string != selected_userData[1]:
                            warningText_string = selected_userData[1]
                        else:
                            os.remove(f"{saveFile_drive}:/2048userdata/{warningText_string}")
                            SaveName_string = ""
                            warningText_string = ""

                elif page == "easteregg2" and cursor.colliderect(startBtn):
                    if not show_eastereggInfo:
                        warningText_string = ""
                        show_eastereggInfo = True
                    elif show_eastereggInfo and TimerVariable < time.time():
                        print("Initiating secrets")
                        page_flashbangValue = 255
                        TimerVariable = time.time() + 5
                        startBtn.size = (270, 50)
                        page = "easteregg3"
                        for key in incrementBtn:
                            for i in range(2):
                                incrementBtn[key][i].size = 30,30

                elif page == "easteregg3":
                    for key in incrementBtn:
                        for i in range(2):
                            if cursor.colliderect(incrementBtn[key][i]):
                                if key == "minus" and (7,0)[i] < startuplock_Settings[list(startuplock_Settings)[i]]:
                                    startuplock_Settings[list(startuplock_Settings)[i]] -= 1
                                elif key == "plus" and startuplock_Settings[list(startuplock_Settings)[i]] < (10, 5)[i]:
                                    startuplock_Settings[list(startuplock_Settings)[i]] += 1
                    
                    if cursor.colliderect(startBtn) and TimerVariable < time.time():
                        activate_StartupLock(startuplock_Settings["TIMER"], startuplock_Settings["SCORE"])
                        page = "easteregg4"
                        warningText_string = ""
                        page_flashbangValue = 255
                        TimerVariable = time.time() + 2
                
                elif page == "easteregg4" and cursor.colliderect(startBtn) and SLdelete_warn[0] != "DELETED":
                    SLdelete_warn = [delete_StartupLock(), 0]

                if cursor.colliderect(creditTextRect):
                    webbrowser.open_new_tab("https://github.com/sidharta310312" if KeySequenceIndex == 0 else "https://en.wikipedia.org/wiki/Konami_Code")

            if event.type == pygame.KEYDOWN and page == "gameTime":
                keyName = pygame.key.name(event.key)
                directions = {"left":("x", 0),
                            "right":("x", 1),
                            "up":("y", 0),
                            "down":("y", 1)}
                
                if keyName in "wasd":
                    keyName = {"w":"up",
                            "a":"left",
                            "s":"down",
                            "d":"right"}[keyName]

                if keyName in list(directions):
                    CurrentAxis = directions[keyName][0]
                    CurrentDirection = directions[keyName][1]

                    if CurrentAxis == "x":
                        for row_index, row in enumerate(numOccup):
                            numOccup[row_index] = CombineNumbers(row, CurrentDirection)

                    elif CurrentAxis == "y":
                        RotatedBoard = [] #Up to Down on Normal Board = Left to Right on Rotated Board
                        for i in range(boardSize[0]):
                            RotatedBoard.append([])
                            for j in range(boardSize[1]):
                                RotatedBoard[i].append(numOccup[j][i])
                        
                        #print(f"Rotated board : {RotatedBoard}")
                        for column_index, column in enumerate(RotatedBoard):
                            RotatedBoard[column_index] = CombineNumbers(column, CurrentDirection)
                        
                        for i in range(boardSize[0]):
                            for j in range(boardSize[1]):
                                numOccup[j][i] = RotatedBoard[i][j]

                    if 0 in UnpackSublists(numOccup):
                        numOccup, newblock_flashbangValue["Position"] = AddRandomNumber(numOccup)
                        newblock_flashbangValue["Opacity"] = 255
                    elif not 0 in UnpackSublists(numOccup) and not gameover:
                        #Check gameover
                        gameover = True
                        for row in numOccup:
                            for item_index in range(len(row)):
                                if item_index < len(row) - 1 and gameover:
                                    gameover = not row[item_index] == row[item_index + 1]
                        
                        for i in range(boardSize[0]):
                            for j in range(boardSize[1]):
                                if j < boardSize[1] - 1 and gameover:
                                    gameover = not numOccup[j][i] == numOccup[j + 1][i]
                        
                        if gameover:
                            TimerVariable += time.time() - timeStarted
                            show_gameoverTip = time.time() + 2.3
                            
                            page_flashbangValue = 255


                    currentScore = max(UnpackSublists(numOccup))
                    ArrowKeyPressed = keyName.upper() + "_ARROW"
                    movesMade += 1 if not gameover else 0
                    print(f"IS GAMEOVER? {gameover}, BOARD DATA = {numOccup}")
            
            if event.type == pygame.KEYDOWN and page == "savingGame":
                keyName = pygame.key.name(event.key)
                if not twoStep_SNverification:
                    if keyName in string.ascii_letters + string.digits and len(SaveName_string) < 16:
                        SaveName_string += keyName
                    elif event.key == pygame.K_BACKSPACE:
                        SaveName_string = SaveName_string[:-1]
                else:
                    if keyName == "left":
                        data = {"boardSize":boardSize,
                                "boardData":numOccup,
                                "Timer" : TimerVariable + time.time() - timeStarted,
                                "MovesMade":movesMade,
                                "LastPlayed":str(datetime.now().date())}
                        
                        SaveData(SaveName_string, data)
                        
                        page = "gameTime"
                        warningText_string = f"Saved successfully as {SaveName_string}.json"
                        SaveAlert_time = time.time() + 3
                    elif keyName == "right":
                        twoStep_SNverification = False

            if event.type == pygame.KEYDOWN and page == "start":
                keyName = pygame.key.name(event.key)
                if keyName == targetSequence[KeySequenceIndex]:
                    KeySequenceIndex += 1
                else:
                    KeySequenceIndex = 0
                
                print("User key sequence : " , KeySequenceIndex)
                

                if KeySequenceIndex == len(targetSequence):
                    print("User has discovered the easter egg")
                    page = "easteregg" if not check_winreg() else "easteregg4"
                    page_flashbangValue = 255
                    warningText_Ypos = 0
                    KeySequenceIndex = 0
                    creditText_xpos = 200
            
    

    if page == "start":
        for index, Ypos in enumerate(icons_transitionPos): #RENDERING ICONS
            rect = iconRects[index]
            margin = (rect.size[0] * 1.2) #Icon margin
            
                
            rect.topleft = (centerPos[0] - (rect.size[0] * 2) - (margin//4)) + (index * margin), Ypos
            pygame.draw.rect(screen, (red, green, yellow, blue)[index], rect)

            MakeText("2048"[index], 50, white, rect.center, True)


        if icons_transitionPos[len(icons_transitionPos) - 1] < 100:
            if icons_transitionPos[icons_transitionIndex] < 100:
                icons_transitionPos[icons_transitionIndex] += 10
            else:
                if icons_transitionIndex != len(icons_transitionPos) - 1:
                    icons_transitionIndex += 1
                
            #if icons_transitionPos[len(icons_transitionPos) - 1] >= 100:
            #    transition = False
                

        else:
            for jndex, rect in enumerate(iconRects):
                margin = (rect.size[0] * 1.2)
                rect_OriginPos = (centerPos[0] - (rect.size[0] * 2) - (margin//4)) + (jndex * margin), 100

                shakeEffex = [(icon_flashbang[jndex]/255) * random.randint(-10,10), (icon_flashbang[jndex]/255) * random.randint(-10,10)]

                iconRects[jndex].topleft = rect_OriginPos[0] + shakeEffex[0], rect_OriginPos[1] + shakeEffex[1]

                flashbang = pygame.Surface(rect.size, pygame.SRCALPHA)
                flashbang.fill((255, 255, 255, icon_flashbang[jndex]))

                if icon_flashbang[jndex] > 0:
                    icon_flashbang[jndex] -= 1
                else:
                    icon_flashbang[jndex] = 0

                screen.blit(flashbang, rect)
        

        #startBtn.center = centerPos
        loadBtn.center = centerPos[0], centerPos[1] + 100

        pygame.draw.rect(screen, taupeColor, startBtn)
        pygame.draw.rect(screen, darkTaupe, loadBtn)

        distanX = cursor.centerx - centerPos[0]
        distanY = cursor.centery - centerPos[1]

        startBtn.center = (centerPos[0] + (distanX/40), centerPos[1] + (distanY/40))

        MakeText("NEW GAME" if numOccup == [] else "CONTINUE", {"True": 45, "False": 40}[str(startBtn.colliderect(cursor))], white, (centerPos[0] + (distanX/15), centerPos[1] + (distanY/15)), startBtn.colliderect(cursor))
        MakeText("OR LOAD SAVE-FILE", {"True": 24, "False": 20}[str(loadBtn.colliderect(cursor))], white, loadBtn.center, loadBtn.colliderect(cursor))
        if numOccup != []:
            newGameBtn = MakeText("Start new game", 30, darkBlue if cursor.colliderect(newGameBtn) else blue, (centerPos[0], centerPos[1] + 200), True)
            if cursor.colliderect(newGameBtn):
                pygame.draw.rect(screen, darkBlue, pygame.Rect([newGameBtn.bottomleft[helloworld] - (0, 10)[helloworld] for helloworld in range(0,2)], (newGameBtn.size[0] , 2)))
    
    elif page == "newGame":
        SaveName_string = ""
        MakeText("NEW GAME", 80, darkTaupe, (centerPos[0], 100), True)

        MakeText("set board size", 30, darkTaupe, (centerPos[0], 160), True)
        #Display increment buttons
        for btnType in incrementBtn:
            for index, chosenBtn in enumerate(incrementBtn[btnType]):
                chosenBtn.center = centerPos[0] + [-130,130][index], centerPos[1] + {"plus":-100, "minus":100}[btnType]
                if chosenBtn.colliderect(cursor):
                    pygame.draw.rect(screen, {"plus":darkGreen, "minus":darkRed}[btnType], chosenBtn)
                else:
                    pygame.draw.rect(screen, {"plus":green, "minus":red}[btnType], chosenBtn)

                MakeText({"plus":"+", "minus":"-"}[btnType], 30, white, chosenBtn.center, chosenBtn.colliderect(cursor))

        #Display board size
        for index, size in enumerate(boardSize):
            textPos = centerPos[0] + [-130,130][index], centerPos[1]
            #MakeText(str(boardSize[index]), 40, taupeColor, textPos, False)
            size_Text = MakeText(str(size), 40, taupeColor, textPos, False)
            MakeText({"0":"width", "1":"height"}[str(index)],
                     20,
                     darkTaupe,
                     (size_Text.center[0], size_Text.center[1] + 50),
                     cursor.colliderect(incrementBtn["plus"][index]) or cursor.colliderect(incrementBtn["minus"][index]))

        startBtn.center = centerPos[0], centerPos[1] + 250
        pygame.draw.rect(screen, {"True":darkTaupe, "False":taupeColor}[str(startBtn.colliderect(cursor))], startBtn)
        MakeText("LETS PLAY!", 30, white, startBtn.center, startBtn.colliderect(cursor))

        if page_flashbangValue > 0:
            p_fbSurface = pygame.Surface(screensize,pygame.SRCALPHA)
            p_fbSurface.fill((255,255,255,page_flashbangValue))
            screen.blit(p_fbSurface, (0,0))

            if page_flashbangValue > 0:
                page_flashbangValue -= 1

    elif page == "gameTransition":
        if round(startBtn.center[1]) > centerPos[1] - 50:
            startBtn.center = startBtn.center[0], startBtn.centery - (startBtn.center[1] - (centerPos[1]-50))/20
            pygame.draw.rect(screen, darkTaupe, startBtn)
        elif int(startBtn.size[0]) <= 500:
            #print(startBtn.size)
            startBtn.center = centerPos[0], centerPos[1] - 50
            startBtn.size = startBtn.size[0] + ((550 - startBtn.size[0])*0.1), startBtn.size[1]
            pygame.draw.rect(screen, darkTaupe, startBtn)
        elif startBtn.size[1] <= 500:
            startBtn.size = 500, startBtn.size[1] + ((550 - startBtn.size[1]) * 0.07)
            startBtn.centery = centerPos[1] - 50
            pygame.draw.rect(screen, darkTaupe, startBtn)
        else:
            timeStarted = time.time()
            page = "gameTime"

    elif page == "gameTime":
        #print(numOccup)
        boardPosition, fb_nb_size = RenderBoard(numOccup)

        startBtn.center = centerPos[0], screensize[1] - 100
        startBtn.size = (200,75)
        
        if not gameover:
            pygame.draw.rect(screen, {"False":taupeColor, "True":darkTaupe}[str(startBtn.colliderect(cursor))], startBtn)
            MakeText("SAVE GAME", 30, white, startBtn.center, startBtn.colliderect(cursor))
        else:
            MakeText("GAMEOVER", 40, red, startBtn.center, startBtn.colliderect(cursor))
            if show_gameoverTip < time.time():
                newGameBtn = MakeText("New game", 20, blue, (startBtn.center[0], startBtn.center[1] + 40), startBtn.colliderect(cursor))
                if cursor.colliderect(newGameBtn):
                    pygame.draw.rect(screen, blue, pygame.Rect([newGameBtn.bottomleft[IncrementThingy] - (0, 7)[IncrementThingy] for IncrementThingy in range(0,2)], (newGameBtn.size[0] , 2)))

        MakeText(f"Score : {("none lmao", 1 << currentScore)[int(currentScore!=0)]}", 20, darkTaupe, (startBtn.center[0] - 250, startBtn.center[1]), startBtn.colliderect(cursor))
        MakeText(f"Moves Made : {("none lmao", movesMade)[int(movesMade>0)]}", 20, darkTaupe, (startBtn.center[0] + 250, startBtn.center[1]), startBtn.colliderect(cursor))
        MakeText(FormatTime(time.time() - timeStarted + TimerVariable if not gameover else TimerVariable), 30, darkTaupe, (centerPos[0], centerPos[1] - 350), True)
        MakeText(str(boardSize[0]), 10, darkTaupe, (centerPos[0], boardPosition[1] - 20), False)
        MakeText(str(boardSize[1]), 10, darkTaupe, (boardPosition[0] - 20, centerPos[1] - 50), False)

        HomeIcon_rect.topright = screensize[0] - 20, 20
        imageSurfaces["HOMEICON"].set_alpha(255 if cursor.colliderect(HomeIcon_rect) else 128)
        screen.blit(imageSurfaces["HOMEICON"], HomeIcon_rect)

        if SaveAlert_time > time.time():
            rectangle = pygame.Surface([x + (60 - (SaveAlert_time - time.time()) * 20) for x in MakeText(warningText_string, 20, red if warningText_string == f"Drive {saveFile_drive} required to save games" else green, (centerPos[0], 25), True).size], pygame.SRCALPHA)
            rectangle.fill(list(red if warningText_string == f"Drive {saveFile_drive} required to save games" else green) + [(SaveAlert_time - time.time()) * 80])
            screen.blit(rectangle, [(centerPos[0], 25)[x] - (rectangle.size[x] // 2) for x in range(2)])


        for index, keyName in enumerate(list(imageSources)[0:4]):
            key = imageSurfaces[keyName]
            key.set_alpha(255 if keyName == ArrowKeyPressed else 128)
            screen.blit(key, (40*index, 50) if keyName != "UP_ARROW" else (40, 10))

        if page_flashbangValue > 0:
            if not gameover:
                p_fbSurface = pygame.Surface((500,500),pygame.SRCALPHA)
                p_fbSurface.fill((255,255,255,page_flashbangValue))
                screen.blit(p_fbSurface, (centerPos[0] - 250,centerPos[1] - 300))
            else:
                imageSurfaces["SKILLISSUE"].set_alpha(page_flashbangValue)
                screen.blit(imageSurfaces["SKILLISSUE"], [(centerPos[0], centerPos[1] - 50)[x] - (imageSurfaces["SKILLISSUE"].get_size()[x] // 2) for x in range(2)])

            page_flashbangValue -= 1 if not gameover else 5

        if newblock_flashbangValue["Opacity"] > 0:
            fb_margin = 80/boardSize[0]   
            fb_SizeIncrease = 20 - 20*((newblock_flashbangValue["Opacity"]/255))
            newblock_fb = pygame.Surface(tuple([x + fb_SizeIncrease for x in fb_nb_size]), pygame.SRCALPHA)

            newblock_fb.fill((0,0,0, newblock_flashbangValue["Opacity"]))

            X_fb = newblock_flashbangValue["Position"][0]
            Y_fb = newblock_flashbangValue["Position"][1]

            #nb_fb_position = (boardPosition[0] + (X_fb * (fb_nb_size[0] + fb_margin)) + (fb_margin/2),
            #                     boardPosition[1] + (Y_fb * (fb_nb_size[1] + fb_margin)) + (fb_margin/2))

            nb_fb_position = [boardPosition[enrique] + (newblock_flashbangValue["Position"][enrique] * (fb_nb_size[enrique] + fb_margin)) + (fb_margin/2) - (fb_SizeIncrease/2) for enrique in range(0,2)]
            print(nb_fb_position)

            #newTile = pygame.Rect(boardRect.topleft, tileSize)
            #newTile.topleft = newTile.topleft[0] + (margin * X_pos) + (X_pos * tileSize[0]) + (margin/2),newTile.topleft[1] + (margin * Y_pos) + (Y_pos * tileSize[1]) + (margin/2)
                

            screen.blit(newblock_fb, nb_fb_position)
            newblock_flashbangValue["Opacity"] -= 5

        #pygame.draw.rect(screen, darkTaupe, startBtn)

    elif page == "warn":
        for index in range(0,4): #RENDERING ICONS
            rect = iconRects[index]
            margin = (rect.size[0] * 1.2) #Icon margin
                
            rect.topleft = (centerPos[0] - (rect.size[0] * 2) - (margin//4)) + (index * margin), 100
            pygame.draw.rect(screen, (red, green, yellow, blue)[index], rect)

            MakeText("2048"[index], 50, white, rect.center, True)
        
        
        warningImage = imageSurfaces["DANGERSIGN"]
        warningImage_rect = warningImage.get_rect(center=[centerPos[x] + ((page_flashbangValue/255) * random.randint(-30,30)) for x in range(0,2)])
        screen.blit(warningImage, warningImage_rect)

        warningImage_flashbang = pygame.Surface(warningImage.get_size(), pygame.SRCALPHA)
        warningImage_flashbang.fill((255,255,255, page_flashbangValue))
        screen.blit(warningImage_flashbang, warningImage_rect)

        if page_flashbangValue > 0:
            page_flashbangValue -= 5
        
        MakeText("Warning", int(50 * (warningText_Ypos/300)), yellow, (centerPos[0], warningText_Ypos), True)
        warningText_Ypos += (warningText_Ypos - 300) *-0.05

        MakeText(warningText_string, 30, darkTaupe, (centerPos[0], centerPos[1] + 150), False)

        if page_flashbangValue < 100:
            fulltext = "Creating a new game will erase data from\nyour previous game (woohh sangat ngeri)"
            if len(warningText_string) < len(fulltext):
                warningText_string = warningText_string + fulltext[len(warningText_string)]
            else:
                for index, btn in enumerate(warnBtnChoices):
                    btn.center = (centerPos[0], centerPos[1] + (250,330)[index])
                    pygame.draw.rect(screen, (green, red)[index] if not cursor.colliderect(btn) else (darkGreen, darkRed)[index], btn)
                    MakeText(["new game", "nevermind"][index], 20, white, btn.center, cursor.colliderect(btn))

    elif page == "savingGame":
        HomeIcon_rect.topright = screensize[0] - 20, 20
        imageSurfaces["HOMEICON"].set_alpha(255 if cursor.colliderect(HomeIcon_rect) else 128)
        screen.blit(imageSurfaces["HOMEICON"], HomeIcon_rect)


        #warningText_Ypos = 0
        boardPosition = RenderBoard(numOccup)[0]
        saveGame_heading = pygame.font.SysFont("georgia", 30).render("CREATING NEW SAVE FILE", True, darkTaupe)
        screen.blit(saveGame_heading, (boardPosition[0], boardPosition[1] - warningText_Ypos))
        if warningText_Ypos > 35:
            warningText_Ypos -= 2
        
        
        MakeText((f"{SaveName_string}_" if int(time.time()) % 2 == 0 else SaveName_string, "Type your save file [Max 16 char.]")[int(len(SaveName_string) < 1)], 30, darkTaupe, (centerPos[0], screensize[1] - 50), False)

        if startBtn.centery > 650:
            startBtn.centery += (650 - startBtn.centery) * 0.1
        
        pygame.draw.rect(screen, darkTaupe if cursor.colliderect(startBtn) else taupeColor, startBtn)
        MakeText("NEED NAME PLS" if SaveAlert_time > time.time() else "SAVE GAME", 20, white, startBtn.center, cursor.colliderect(startBtn))

        if twoStep_SNverification:
            MakeText(f"{SaveName_string}.json already exists! Want to replace it?", 20, darkTaupe, (centerPos[0], page_flashbangValue), True)
            if page_flashbangValue < 30:
                page_flashbangValue += 1
            else:
                for i in range(2):
                    position = (160 + (i * 100), 50)
                    screen.blit(imageSurfaces[("LEFT_ARROW", "RIGHT_ARROW")[i]], [position[x] - 15 for x in range(2)])
                    MakeText(["YES", "NO"][i], 20, taupeColor, (position[0] + 35, position[1]), False)

        if SaveAlert_time > time.time():
            sizeIncrement = 100 - ((SaveAlert_time - time.time())*100)
            flashbang = pygame.Surface([x + sizeIncrement for x in startBtn.size], pygame.SRCALPHA)
            flashbang.fill((255,0,0, (SaveAlert_time - time.time())*51))
            flashbang_size = flashbang.get_size()
            screen.blit(flashbang, [startBtn.center[x] - (flashbang_size[x] // 2) for x in range(2)])
    
    elif page == "loadFile":
        MakeText("LOAD GAME", 80, darkTaupe, (centerPos[0], 100), True)

        HomeIcon_rect.topright = screensize[0] - 20, 20
        imageSurfaces["HOMEICON"].set_alpha(255 if cursor.colliderect(HomeIcon_rect) else 128)
        screen.blit(imageSurfaces["HOMEICON"], HomeIcon_rect)

        if len(allJSON_files) > 0:
            for index, key in enumerate(list(loadGame_pagebuttons)):
                loadGame_pagebuttons[key].center = centerPos[0] + (-150,150)[index], screensize[1] - 120
                pygame.draw.rect(screen, darkYellow if cursor.colliderect(loadGame_pagebuttons[key]) else yellow, loadGame_pagebuttons[key])
                MakeText(("PREVIOUS", "NEXT")[index], 20, white, loadGame_pagebuttons[key].center, cursor.colliderect(loadGame_pagebuttons[key]))
            
            MakeText("page", 12, darkYellow, (centerPos[0], screensize[1] - 135), True)
            MakeText(f"{userData_page + 1}/{math.ceil(len(allJSON_files)/5)}", 25, darkYellow, (centerPos[0], screensize[1] - 115), True)

        if not Path(f"{saveFile_drive}:/").is_dir():
            screen.blit(imageSurfaces["SKILLISSUE"], [centerPos[x] - (imageSurfaces["SKILLISSUE"].get_size()[x] // 2) for x in range(2)])
            MakeText("SKILL ISSUE", 30, red, (centerPos[0], centerPos[1] + 140), True)
            MakeText(f"Drive {saveFile_drive} required to save games", 10, red, (centerPos[0], centerPos[1] + 160), True)
        else:
            if len(allJSON_files) > 0:
                for index, file in enumerate(allJSON_files[userData_page*5:(userData_page + 1) * 4 + 1]):
                    #if index >= userData_page*4 and index <= (userData_page + 1) * 4:
                    thingy = pygame.Rect(0,0, screensize[0] - 250, 90)
                    thingy.center = centerPos[0], 180 + (thingy.size[1] * 1.1 * index)

                    if ReadJSON(file) != "NOTFOUND":
                        pygame.draw.rect(screen, darkTaupe if not cursor.colliderect(thingy) else taupeColor, thingy)
                        fileName_text = pygame.font.SysFont("microsofttaile", 20).render(file, True, white)
                        screen.blit(fileName_text, [x + 10 for x in thingy.topleft])
                    else:
                        pygame.draw.rect(screen, red if not cursor.colliderect(thingy) else darkRed, thingy)
                        fileName_text = pygame.font.SysFont("microsofttaile", 20).render(file + " not found \n(probably deleted)", True, white)
                        screen.blit(fileName_text, [x + 10 for x in thingy.topleft])
                        continue

                    if cursor.colliderect(thingy):
                        selected_userData = ReadJSON(file)
                        
                        fileDesc_text = pygame.font.SysFont("mingliuextb", 14).render(f"Time spent : {FormatTime(selected_userData[0]["Timer"])} \nHigh Score : {1 << max(UnpackSublists(selected_userData[0]["boardData"]))} \nBoard Size = {selected_userData[0]["boardSize"]}", True, white)
                        screen.blit(fileDesc_text, [thingy.topleft[x] + (10,35)[x] for x in range(2)])

                        
                        imageSurfaces["PLAYBTN"].set_alpha(255 if cursor.colliderect(loadGame_btns["PLAY"]) else 128)
                        screen.blit(imageSurfaces["PLAYBTN"], [(thingy.center[0] * 1.4, thingy.center[1])[iranoutofvariablenames] - (imageSurfaces["PLAYBTN"].get_size()[iranoutofvariablenames] // 2) for iranoutofvariablenames in range(2)])
                        loadGame_btns["PLAY"] = imageSurfaces["PLAYBTN"].get_rect(center=(thingy.center[0] * 1.4, thingy.center[1]))

                        loadGame_btns["DELETE"] = pygame.draw.circle(screen, darkRed if cursor.colliderect(loadGame_btns["DELETE"]) else red, (thingy.center[0] * 1.6, thingy.center[1]), 30)
                        MakeText("DELETE" if file != warningText_string else "U SURE?", 11, white, (thingy.center[0] * 1.6, thingy.center[1]), cursor.colliderect(loadGame_btns["DELETE"]))

                        #Render Button Hitboxes   
                        #for index, key in enumerate(list(loadGame_btns)):
                        #    pygame.draw.rect(screen, (green,red)[index], loadGame_btns[key])
                    else:
                        MakeText("FILE NO. " + str(index + 1 + (userData_page*5)), 25, white, (thingy.center[0] * 1.5, thingy.center[1]), False)
                        unselected_userData = ReadJSON(file)[0]
                        fileDesc_text = pygame.font.SysFont("mingliuextb", 14).render(f"Last played : {"today" if unselected_userData["LastPlayed"] == str(datetime.now().date()) else unselected_userData["LastPlayed"]}", True, white)
                        screen.blit(fileDesc_text, [thingy.topleft[x] + (10,35)[x] for x in range(2)])
            else: #If theres no save files
                thingy = pygame.Rect(0,0, screensize[0] - 250, 90)
                thingy.center = centerPos[0], 180
                pygame.draw.rect(screen, darkTaupe if not cursor.colliderect(thingy) else taupeColor, thingy)

                fileName_text = pygame.font.SysFont("microsofttaile", 20).render("wherefile.json", True, white)
                screen.blit(fileName_text, [x + 10 for x in thingy.topleft])

                fileDesc_text = pygame.font.SysFont("mingliuextb", 14).render("no save files found?", True, white)
                screen.blit(fileDesc_text, [thingy.topleft[x] + (10,35)[x] for x in range(2)])

                imageSurfaces["SKILLISSUE"].set_alpha(128)

                screen.blit(pygame.transform.scale(imageSurfaces["SKILLISSUE"], (64, 64)), [heru - 32 for heru in (thingy.center[0] * 1.5, thingy.center[1])])

                loadGame_btns["PLAY"] = imageSurfaces["PLAYBTN"].get_rect(size = (play_btn_size, play_btn_size))
                loadGame_btns["PLAY"].center = (centerPos[0], centerPos[1] +250)
                screen.blit(pygame.transform.scale(imageSurfaces["PLAYBTN"], (play_btn_size, play_btn_size)), loadGame_btns["PLAY"])

                if cursor.colliderect(loadGame_btns["PLAY"]) and play_btn_size < 140:
                    play_btn_size += 1
                elif not cursor.colliderect(loadGame_btns["PLAY"]) and play_btn_size > 128:
                    play_btn_size -= 1

                MakeText("Create new save file", 30, taupeColor, (loadGame_btns["PLAY"].center[0], loadGame_btns["PLAY"].center[1] - 90), cursor.colliderect(loadGame_btns["PLAY"]))


        if page_flashbangValue > 0:
            p_fbSurface = pygame.Surface(screensize,pygame.SRCALPHA)
            p_fbSurface.fill((255,255,255,page_flashbangValue))
            screen.blit(p_fbSurface, (0,0))

            if page_flashbangValue > 0:
                page_flashbangValue -= 1

    elif page == "easteregg":
        if page_flashbangValue > 0:
            thingy = pygame.Surface(screensize, pygame.SRCALPHA)
            thingy.fill((255,255,255,page_flashbangValue))
            screen.blit(thingy, (0,0))
            page_flashbangValue -= 1
            if page_flashbangValue <= 0:
                TimerVariable = time.time() + 2
                print(TimerVariable - time.time())
        else:
            headingText = MakeText("STARTUP LOCK MODE SETTINGS", 20 + int(10 * (warningText_Ypos / 300)), white, (centerPos[0], centerPos[1] - warningText_Ypos), False)
            if TimerVariable - 1.5 < time.time():
                thingy = pygame.Surface((screensize[0], headingText.size[1]), pygame.SRCALPHA)
                thingy.fill((255,255,255, int((time.time() % 1) * 255) if (time.time() % 2) < 1 else 255 - int((time.time() % 1) * 255)))
                screen.blit(thingy, [headingText.center[i] - (thingy.get_size()[i]//2) for i in range(2)])
            
            if TimerVariable < time.time() and warningText_Ypos < 300:
                warningText_Ypos += 2
            elif warningText_Ypos >= 300:
                page = "easteregg2"
                page_flashbangValue = screensize[0] // 2 #not really used for flashbang effect, but this time used for text hovering effect
    
    elif page == "easteregg2":
        if not show_eastereggInfo:
            startBtn = MakeText("Click me for info (IMPORTANT)", 20, darkBlue if cursor.colliderect(startBtn) else white, (centerPos[0] - page_flashbangValue, 180), False)
            if cursor.colliderect(startBtn):
                pygame.draw.rect(screen, darkBlue, (startBtn.topleft[0], startBtn.bottomleft[1] - 3, startBtn.size[0], 2))
        else:
            MakeText(warningText_string, 20, white, (centerPos[0], 150 + (warningText_string.count("\n") * 20)), False)
            fullString = "When STARTUP LOCK MODE is activated, your computer will\nbe locked everytime you boot it up, and you have to\ncomplete a 2048 puzzle just to use your PC\n\n(perfect for trolling friends)"
            if warningText_string != fullString:
                warningText_string += fullString[len(warningText_string)]
                if len(warningText_string) == len(fullString):
                    TimerVariable = time.time() + 1
            else:
                if time.time() > TimerVariable:
                    startBtn = pygame.Rect(0,0,150, 50)
                    startBtn.center = centerPos[0], centerPos[1] + 250
                    pygame.draw.rect(screen, darkGreen if cursor.colliderect(startBtn) else green, startBtn)
                    MakeText("OPEN SETTINGS", 20, white, startBtn.center, cursor.colliderect(startBtn))

        if page_flashbangValue > 0:
            page_flashbangValue -= page_flashbangValue * 0.1

    elif page == "easteregg3":
        InterfacePos = (page_flashbangValue / 255) * centerPos[0]

        setting1_heading = MakeText("Set minimum score requirement to unlock PC", 25, white, (centerPos[0], (centerPos[1] * 0.8) + startuplock_UIpos[0]), False)
        setting1_valueText = pygame.font.SysFont("mvboli", 20).render(f"CURRENT VALUE = {1 << startuplock_Settings["SCORE"]}", True, yellow)
        setting1_valueRect = setting1_valueText.get_rect(topleft=(setting1_heading.topleft[0], setting1_heading.bottomleft[1] + 50 * (startuplock_UIpos[0] / centerPos[0]*0.8)))
        screen.blit(setting1_valueText, setting1_valueRect)
        for index, key in enumerate(["plus", "minus"]): #startuplock_UIpos = [centerPos[1] * 0.8, centerPos[1] * 1.2, centerPos[1] * 1.6]
            incrementBtn[key][0].topleft = setting1_valueRect.topright[0] + 10 + (index * 40), setting1_valueRect.topright[1]
            pygame.draw.rect(screen, [darkGreen, darkRed][index] if cursor.colliderect(incrementBtn[key][0]) else [green, red][index], incrementBtn[key][0])
            MakeText(["+", "-"][index], 20, white, incrementBtn[key][0].center, cursor.colliderect(incrementBtn[key][0]))

        setting2_heading = MakeText("Set timer limit (extra intimidation)", 25, white, (centerPos[0], (centerPos[1] * 1.2) + startuplock_UIpos[1]), False)
        setting2_valueText = pygame.font.SysFont("mvboli", 20).render(f"CURRENT VALUE = {startuplock_Settings["TIMER"]} minutes" if startuplock_Settings["TIMER"] > 0 else "CURRENT VALUE : NO TIMER    ", True, yellow)
        setting2_valueRect = setting2_valueText.get_rect(topleft=(setting2_heading.topleft[0], setting2_heading.bottomleft[1] + 50 * (startuplock_UIpos[1] / centerPos[0]*1.2)))
        screen.blit(setting2_valueText, setting2_valueRect)
        for index, key in enumerate(["plus", "minus"]): #incrementBtn = {"plus":(pygame.Rect(0,0,75,75), pygame.Rect(0,0,75,75)), "minus":(pygame.Rect(0,0,75,75), pygame.Rect(0,0,75,75))}
            incrementBtn[key][1].topleft = setting2_valueRect.topright[0] + 10 + (index * 40), setting2_valueRect.topright[1]
            pygame.draw.rect(screen, [darkGreen, darkRed][index] if cursor.colliderect(incrementBtn[key][1]) else [green, red][index], incrementBtn[key][1])
            MakeText(["+", "-"][index], 20, white, incrementBtn[key][1].center, cursor.colliderect(incrementBtn[key][1]))

        for index in range(len(startuplock_UIpos)):
            if TimerVariable > time.time() and index == 2:
                continue
            startuplock_UIpos[index] -= startuplock_UIpos[index] * 0.05 if int(startuplock_UIpos[index]) > 0 else 0

        startBtn.center = centerPos[0], (centerPos[1] * 1.6) + startuplock_UIpos[2]
        pygame.draw.rect(screen, darkGreen if cursor.colliderect(startBtn) else green, startBtn)
        MakeText("Enable STARTUP LOCK MODE", 20, white, startBtn.center, cursor.colliderect(startBtn))

        spaceHold = pygame.key.get_pressed()[pygame.K_SPACE]
        MakeText("Press [SPACE] to reset settings", 13, white, (startBtn.center[0], startBtn.center[1] + 40), spaceHold)
        if spaceHold:
            startuplock_Settings["SCORE"], startuplock_Settings["TIMER"] = 8,0

        if page_flashbangValue > 0:
            flashbang = pygame.Surface(screensize, pygame.SRCALPHA)
            flashbang.fill([page_flashbangValue]*4)
            screen.blit(flashbang, (0,0))
            page_flashbangValue -= 2

    elif page == "easteregg4":
        maintext = MakeText("STARTUP LOCK MODE SUCCESSFULLY ESTABLISHED", 20, white, centerPos, False)

        if TimerVariable < time.time():
            MakeText(warningText_string, 10, yellow, (centerPos[0], centerPos[1] + 30), False)
            fulltext = "You may safely close the program"
            if warningText_string != fulltext:
                warningText_string += fulltext[len(warningText_string)]
                if warningText_string == fulltext:
                    startBtn.size = (120,40)
                    startBtn.center = centerPos[0], screensize[1] - 100
            else:
                if SLdelete_warn[0] != "DELETED":
                    pygame.draw.rect(screen, darkRed if cursor.colliderect(startBtn) else red, startBtn)
                    MakeText("DISABLE MODE", 15, white, startBtn.center, cursor.colliderect(startBtn))
                
                if SLdelete_warn[0] != "":
                    warning_string = {"DELETED":"Successfully disabled STARTUP LOCK MODE", "NOTFOUND":"STARTUP LOCK MODE has already been deleted", "PERMISSIONERROR":"Access denied, please delete the Windows Registry manually"}[SLdelete_warn[0]]
                    MakeText(warning_string[0:SLdelete_warn[1]], 15, red, (startBtn.center[0], startBtn.center[1] + (50 if SLdelete_warn[0] != "DELETED" else 0)), False)
                    SLdelete_warn[1] += int(len(warning_string) > SLdelete_warn[1])

        if page_flashbangValue > 0:
            size_increment = (100 * ((255 - page_flashbangValue)/255))
            flashbang = pygame.Surface([maintext.size[x] + size_increment for x in range(2)], pygame.SRCALPHA)
            flashbang.fill((255,255,255,page_flashbangValue))
            screen.blit(flashbang, [maintext.topleft[x] - (size_increment // 2) for x in range(2)])
            page_flashbangValue -= 2


    if "easteregg" in page and page != "easteregg": #Make startup lock mode settings header
        headingText = MakeText("STARTUP LOCK MODE SETTINGS", 30, white, (centerPos[0], centerPos[1] - 300), False)
        thingy2 = pygame.Surface((screensize[0], headingText.size[1]), pygame.SRCALPHA)
        thingy2.fill((255,255,255, int((time.time() % 1) * 255) if (time.time() % 2) < 1 else 255 - int((time.time() % 1) * 255)))
        screen.blit(thingy2, [headingText.center[i] - (thingy2.get_size()[i]//2) for i in range(2)])

    creditText = pygame.font.SysFont("copperplategothic", 20, bold=True).render("Made by sidharta310312 on GitHub" if KeySequenceIndex == 0 else f"{KeySequenceIndex}/{len(targetSequence)}", True, taupeColor if not cursor.colliderect(creditTextRect) else darkBlue)
    screen.blit(creditText, (10 - creditText_xpos, screensize[1] - 30))
    creditTextRect = creditText.get_rect(topleft = (10 - creditText_xpos, screensize[1] - 30))
    if cursor.colliderect(creditTextRect):
        pygame.draw.rect(screen, darkBlue, (creditTextRect.bottomleft[0], creditTextRect.bottomleft[1], creditTextRect.size[0], 2))

    if creditText_xpos > 0:
        creditText_xpos -= creditText_xpos * 0.05

    pygame.display.flip()

targetScore = int(sys.argv[sys.argv.index("--startup") + 2]) #in logarithm 

gameloop = True
root = tk.Tk()
root.withdraw()
screensize = (root.winfo_screenwidth(), root.winfo_screenheight())
screen = pygame.display.set_mode(screensize, pygame.FULLSCREEN)
centerPos = [x//2 for x in screensize]

page = "start"
page_flashbangValue = 225
DelayVariable = 0
TimerVariable = 0

icons_transitionPos = [0]*4 #icon transition sizes
icons_maximumSize = 100

dialogs = ["Click this button", "Want to use your computer?", "Solve this 2048 puzzle first", f"Get score {1 << targetScore}" if TimerVariable == 0 else f"Get score {1 << targetScore} in {TimerVariable} minutes","If you try to exit this program...","Your computer will be shutdowned."]
dialog_displayedText = ""
show_dialogIndex = 0
buttonDelay = False



def shutdown():
    print("Shutting down pc")
    os.system("shutdown /s /t 0")

while gameloop: #Startup Lock mode
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if page == "start" and cursor.colliderect(startBtn) and page_flashbangValue <= 0:
                page = "gameTransition"
                DelayVariable = time.time() + 2
                page_flashbangValue = 255
                startBtn.size = (70,30)
                startBtn.center = centerPos[0], centerPos[1] + 77
            if page == "gameTransition" and cursor.colliderect(startBtn) and buttonDelay and DelayVariable < time.time():
                if show_dialogIndex != 1:
                    buttonDelay = False
                    dialog_displayedText = ""
                    show_dialogIndex += 1
                    if show_dialogIndex == len(dialogs):
                        #Initiate game (on Startup lock mode)
                        timeStarted = time.time()
                        page = "gameTime"
                        TimerVariable = int(sys.argv[sys.argv.index("--startup") + 1]) * 60 + time.time()
                        page_flashbangValue = 255
                        numOccup = []
                        for row in range(boardSize[1]):
                            numOccup.append([0]*boardSize[0])
                        numOccup = AddRandomNumber(numOccup)[0]
                else:
                    shutdown()
            if page == "gameCompleted" and cursor.colliderect(startBtn) and DelayVariable + 1 < time.time():
                sys.exit()
                pygame.quit()
        if event.type == pygame.KEYDOWN:
            if page == "gameTransition" and event.key == pygame.K_SPACE and buttonDelay and DelayVariable < time.time() and show_dialogIndex == 1:
                buttonDelay = False
                dialog_displayedText = ""
                show_dialogIndex += 1
            
        if event.type == pygame.KEYDOWN and page == "gameTime" and max(UnpackSublists(numOccup)) < targetScore:
            keyName = pygame.key.name(event.key)
            directions = {"left":("x", 0),
                          "right":("x", 1),
                          "up":("y", 0),
                          "down":("y", 1)}
            
            if keyName in "wasd":
                keyName = {"w":"up",
                           "a":"left",
                           "s":"down",
                           "d":"right"}[keyName]

            if keyName in list(directions):
                CurrentAxis = directions[keyName][0]
                CurrentDirection = directions[keyName][1]

                if CurrentAxis == "x":
                    for row_index, row in enumerate(numOccup):
                        numOccup[row_index] = CombineNumbers(row, CurrentDirection)

                elif CurrentAxis == "y":
                    RotatedBoard = [] #Up to Down on Normal Board = Left to Right on Rotated Board
                    for i in range(boardSize[0]):
                        RotatedBoard.append([])
                        for j in range(boardSize[1]):
                            RotatedBoard[i].append(numOccup[j][i])
                    
                    #print(f"Rotated board : {RotatedBoard}")
                    for column_index, column in enumerate(RotatedBoard):
                        RotatedBoard[column_index] = CombineNumbers(column, CurrentDirection)
                    
                    for i in range(boardSize[0]):
                        for j in range(boardSize[1]):
                            numOccup[j][i] = RotatedBoard[i][j]

                if 0 in UnpackSublists(numOccup):
                    numOccup, newblock_flashbangValue["Position"] = AddRandomNumber(numOccup)
                    newblock_flashbangValue["Opacity"] = 255
                elif not 0 in UnpackSublists(numOccup) and not gameover:
                    #Check gameover
                    gameover = True
                    for row in numOccup:
                        for item_index in range(len(row)):
                            if item_index < len(row) - 1 and gameover:
                                gameover = not row[item_index] == row[item_index + 1]
                    
                    for i in range(boardSize[0]):
                        for j in range(boardSize[1]):
                            if j < boardSize[1] - 1 and gameover:
                                gameover = not numOccup[j][i] == numOccup[j + 1][i]
                    
                    if gameover:
                        page_flashbangValue = 0
                    
                movesMade += 1 if not gameover else 0
                print(f"IS GAMEOVER? {gameover}, BOARD DATA = {numOccup}")

    screen.fill(black)
    FPS_Control.tick(60)
    cursor.center = pygame.mouse.get_pos()

    if page == "start":
        MakeText("STARTUP LOCK", 20, white, centerPos, False)

        #thingy = pygame.Rect(0,0, 10, screensize[1])
        #thingy.center = centerPos
        #pygame.draw.rect(screen, red, thingy)
        
        for index in range(4):
            if icons_transitionPos[index] > 0:
                iconRect = pygame.Rect(0,0,icons_transitionPos[index], icons_transitionPos[index])
                margin = 20
                iconRect.center = (centerPos[0] - (2 * (icons_maximumSize - margin//2))) + (index * (margin + icons_maximumSize)), 150
                pygame.draw.rect(screen, (red, green, yellow, blue)[index], iconRect)

            increase_iconSizes = True
            if icons_transitionPos != [icons_maximumSize]*4:
                for yndex in range(len(icons_transitionPos)):
                    if icons_transitionPos[yndex] < icons_maximumSize and increase_iconSizes:
                        icons_transitionPos[yndex] += 1
                        increase_iconSizes = False
            else:
                icon_flashbang = pygame.Surface((icons_maximumSize + 20 * (page_flashbangValue/255), icons_maximumSize + 20 * (page_flashbangValue/255)), pygame.SRCALPHA)
                icon_flashbang.fill((255,255,255, page_flashbangValue))
                screen.blit(icon_flashbang, [iconRect.topleft[x] - 20 * (page_flashbangValue/255) // 2 for x in range(2)])
                MakeText("2048"[index], 50, white, iconRect.center, True)

                if page_flashbangValue > 0:
                    page_flashbangValue -= 1
                else:
                    startBtn = MakeText("Use my computer", 20, darkBlue if cursor.colliderect(startBtn) else blue, (centerPos[0], centerPos[1] + 30), cursor.colliderect(startBtn))
                    if cursor.colliderect(startBtn):
                        thingy = pygame.Rect(0,0,startBtn.size[0],2)
                        thingy.center = (startBtn.center[0], startBtn.bottomleft[1] - 4)
                        pygame.draw.rect(screen, darkBlue, thingy)
        
    elif page == "gameTransition":
        for index in range(len(icons_transitionPos)):
            iconRect = pygame.Rect(0,0,icons_transitionPos[index], icons_transitionPos[index])
            margin = 20
            iconRect.center = (centerPos[0] - (2 * (icons_maximumSize - margin//2))) + (index * (margin + icons_maximumSize)), 150
            pygame.draw.rect(screen, (red, green, yellow, blue)[index], iconRect)
            MakeText("2048"[index], 50, white, iconRect.center, True)


        if DelayVariable < time.time() and dialog_displayedText != dialogs[show_dialogIndex]:
            dialog_displayedText += dialogs[show_dialogIndex][len(dialog_displayedText)]
        elif dialog_displayedText == dialogs[show_dialogIndex]:
            if not buttonDelay:
                DelayVariable = time.time() + 1  if show_dialogIndex != 4 else time.time() + 1.7
                buttonDelay = True
            elif buttonDelay and DelayVariable < time.time():
                pygame.draw.rect(screen, (darkGreen, darkRed)[int(show_dialogIndex == 1)] if cursor.colliderect(startBtn) else (green, red)[int(show_dialogIndex == 1)], startBtn)
                MakeText("NEXT" if show_dialogIndex != 1 and show_dialogIndex != 5 else ("NO", "I'M READY")[show_dialogIndex == 5], 20 if show_dialogIndex != 5 else 15, white, startBtn.center, cursor.colliderect(startBtn))
                if show_dialogIndex == 1:
                    MakeText("[SPACE] if YES", 10, green, (startBtn.center[0], startBtn.center[1] + 25), False)
        
        MakeText(dialog_displayedText, 20, white, centerPos, False)
    
    elif page == "gameTime":
        for index in range(len(icons_transitionPos)):
            iconRect = pygame.Rect(0,0,icons_transitionPos[index], icons_transitionPos[index])
            margin = 20
            iconRect.center = (centerPos[0] - (2 * (icons_maximumSize - margin//2))) + (index * (margin + icons_maximumSize)), 150
            pygame.draw.rect(screen, (red, green, yellow, blue)[index], iconRect)
            MakeText("2048"[index], 50, white, iconRect.center, True)
        boardpos, fb_nb_size = RenderBoard(numOccup)

        MakeText(f"SCORE : {1 << max(UnpackSublists(numOccup))}/{1 << targetScore}", 20, white, (centerPos[0], centerPos[1] + 300), False)
        MakeText(f"Moves Made : {movesMade}", 20, white, (centerPos[0], centerPos[1] + 325), False)
        if int(sys.argv[sys.argv.index("--startup") + 1]) <= 0:
            MakeText(FormatTime(time.time() - timeStarted), 20, white, (centerPos[0], centerPos[1] + 250), False)
        else:
            MakeText(f"{FormatTime(int(TimerVariable - time.time()))}", 20 if TimerVariable - time.time() > 10 else 20 + int(TimerVariable - time.time()), white if TimerVariable - time.time() > 10 else red, (centerPos[0], centerPos[1] + 250), False)
            if TimerVariable < time.time():
                gameover = True

        if page_flashbangValue > 0:
            board_flashbang = pygame.Surface((500,500), pygame.SRCALPHA)
            board_flashbang.fill((255,255,255,page_flashbangValue))
            screen.blit(board_flashbang, boardpos)
            page_flashbangValue -= 1

        if newblock_flashbangValue["Opacity"] > 0:
            fb_margin = 80/boardSize[0]   
            fb_SizeIncrease = 20 - 20*((newblock_flashbangValue["Opacity"]/255))
            newblock_fb = pygame.Surface(tuple([x + fb_SizeIncrease for x in fb_nb_size]), pygame.SRCALPHA)

            newblock_fb.fill((0,0,0, newblock_flashbangValue["Opacity"]))

            X_fb = newblock_flashbangValue["Position"][0]
            Y_fb = newblock_flashbangValue["Position"][1]

            #nb_fb_position = (boardPosition[0] + (X_fb * (fb_nb_size[0] + fb_margin)) + (fb_margin/2),
            #                     boardPosition[1] + (Y_fb * (fb_nb_size[1] + fb_margin)) + (fb_margin/2))

            nb_fb_position = [boardpos[enrique] + (newblock_flashbangValue["Position"][enrique] * (fb_nb_size[enrique] + fb_margin)) + (fb_margin/2) - (fb_SizeIncrease/2) for enrique in range(0,2)]
            print(nb_fb_position)

            #newTile = pygame.Rect(boardRect.topleft, tileSize)
            #newTile.topleft = newTile.topleft[0] + (margin * X_pos) + (X_pos * tileSize[0]) + (margin/2),newTile.topleft[1] + (margin * Y_pos) + (Y_pos * tileSize[1]) + (margin/2)
                

            screen.blit(newblock_fb, nb_fb_position)
            newblock_flashbangValue["Opacity"] -= 5

        if gameover or max(UnpackSublists(numOccup)) >= targetScore:
            blackout = pygame.Surface(screensize, pygame.SRCALPHA)
            blackout.fill((255,255,255,page_flashbangValue))
            screen.blit(blackout, (0,0))
            page_flashbangValue += 2.5
            if page_flashbangValue >= 255:
                page = "gameCompleted"
                DelayVariable = time.time() + 2
                page_flashbangValue = 0
    
    elif page == "gameCompleted" and DelayVariable < time.time():
        if max(UnpackSublists(numOccup)) >= targetScore:
            MakeText("You win!!", 40, green, centerPos, False)
            if DelayVariable + 1 < time.time():
                startBtn = pygame.Rect(0,0,150,50)
                startBtn.center = centerPos[0], centerPos[1] + 150
                pygame.draw.rect(screen, darkGreen if cursor.colliderect(startBtn) else green, startBtn)
                MakeText("UNLOCK", 30, white, startBtn.center, cursor.colliderect(startBtn))
        else:
            MakeText("You lost.", 40, red, centerPos, False)
            if DelayVariable + 2 < time.time():
                thingy = pygame.Surface(screensize, pygame.SRCALPHA)
                thingy.fill((0, 112, 192, page_flashbangValue))
                screen.blit(thingy, (0,0))
                page_flashbangValue += 2
                if page_flashbangValue >= 255:
                    shutdown()
    
    keys = pygame.key.get_pressed()
    for key in (pygame.K_LALT, pygame.K_RALT, pygame.K_LSUPER, pygame.K_RSUPER, pygame.K_LCTRL, pygame.K_RCTRL):
        if keys[key]:
            screen = pygame.display.set_mode(screensize, pygame.FULLSCREEN)
    
    pygame.display.flip()


