import pygame, math, sys, time
import networkx as nx
from pygame.locals import *
from HeroSprite import *
from nonCharSprite import *
from Button import *
from MonsterSprite import *
import numpy as np
import cv2
import datetime
from MotionTrack import *

lower_green = np.array([29, 86, 6])
upper_green = np.array([64, 255, 255])

BLOCKSIZE = 36
NUMSPACES = 15  #row, col = 15, 20

# modes include: "start", "modeSelection","keyboard", "camera",
#                "instruction", "highScores", "end", "win"

# facilitate the process of recording and reading high scores.
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def recordTime():
    now = datetime.datetime.now()
    year = now.year #int
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    return "%d.%02d.%02d %02d:%02d" % (year, month, day, hour, minute)

class ImageCache:
    def __init__(self):
        self.cache = {}

    def get(self, filename):
        if filename not in self.cache:
            self.cache[filename] = pygame.image.load("data/images/" + filename)
        return self.cache[filename]


imageCache = ImageCache()


class GameStatus:
    def __init__(self):
        self.levelDone = False
        self.points = 0
        self.lives = 3
        self.neatPoints = 0
        self.level = 0
        self.lastLevel = False
        self.pause = False

    def addLife(self, num):
        self.lives += num

    def killLife(self):
        self.lives -= 1

    def addPoints(self, points):
        self.points += points
        self.neatPoints += points
        if self.neatPoints >= 300:
            self.neatPoints -= 300
            self.lives += 1

    def nextLevel(self):
        self.level += 1

    def drawStats(self, screen):
        screen.fill((0, 0, 0))
        font = pygame.font.Font("data/Jokerman.ttf", 25)
        text = font.render(" Level:%2i                          Lives:%2i                          Points: %06i"
                           % (self.level, self.lives, self.points),
                           1, (255, 201, 14))
        textPos = (10, BLOCKSIZE * NUMSPACES + 10)
        screen.blit(text, textPos)

class FoodRushGame:
    def __init__(self):
        pygame.font.init()
        # 20 cols
        self.width = BLOCKSIZE * (NUMSPACES + 5)
        # 15 rows + 50
        self.height = BLOCKSIZE * NUMSPACES + 50

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(50, 50)
        rect = self.screen.get_rect()

        self.mode = "start"
        self.highScores = []
        self.graph = None
        self.loadMonsters("B")
        self.loadMonsters("G")

        pygame.display.set_caption("Food Rush")
        icon = imageCache.get("hero.png")
        pygame.display.set_icon(icon)

    def writeScores(self,path,score):
        time = recordTime()
        scores = readFile(path)
        if scores == "" and score > 0:
            contentsToWrite = "%05d   %s" % (score, time)
            writeFile(path, contentsToWrite)
        else:
            scoresList = scores.split(",")
            if len(scoresList) < 3:
                numList = []
                for i in range(len(scoresList)):
                    items = scoresList[i].split(" ")
                    numList.append(int(items[0]))
                if score > 0:
                    scoresList.append("%05d   %s" % (score, time))
                    contentsToWrite = ",".join(scoresList)
                    writeFile(path, contentsToWrite)
            if len(scoresList) == 3:
                numList = []
                for i in range(len(scoresList)):
                    items = scoresList[i].split(" ")
                    numList.append(int(items[0]))
                minimum = min(numList)
                if score > min(numList):
                    index = numList.index(minimum)
                    scoresList.pop(index)
                    scoresList.append("%05d   %s" % (score, time))
                    contentsToWrite = ",".join(scoresList)
                    writeFile(path, contentsToWrite)

    def readScores(self,path):
        scores = readFile(path)
        if scores == "":
            self.highScores = []
        else:
            scoresList = scores.split(",")
            if len(scoresList) == 1:
                self.highScores = [scoresList[0], "XXXXX", "XXXXX"]
            if len(scoresList) == 2:
                numList = []
                for i in range(2):
                    items = scoresList[i].split(" ")
                    numList.append(int(items[0]))
                maxIndex = numList.index(max(numList))
                minIndex = numList.index(min(numList))
                self.highScores = [scoresList[maxIndex], scoresList[minIndex], "XXXXX"]
            if len(scoresList) == 3:
                numList = []
                for i in range(3):
                    items = scoresList[i].split(" ")
                    numList.append(int(items[0]))
                maxIndex = numList.index(max(numList))
                minIndex = numList.index(min(numList))
                mediumIndex = 3 - maxIndex - minIndex
                self.highScores = [scoresList[maxIndex],scoresList[mediumIndex],scoresList[minIndex]]

    def setStartButtons(self):
        playGameUpImg = imageCache.get("playgameButtonUp.png")
        playGameDownImg = imageCache.get("playgameButtonDown.png")
        howToPlayUpImg = imageCache.get("howtoplayButtonUp.png")
        howToPlayDownImg = imageCache.get("howtoplayButtonDown.png")
        highScoresUpImg = imageCache.get("highscoresButtonUp.png")
        highScoresDownImg = imageCache.get("highscoresButtonDown.png")

        self.playGameButton = Button(playGameUpImg, playGameDownImg,
                                     (self.width *0.75, self.height * 4 / 8 + 100))
        self.howToPlayButton = Button(howToPlayUpImg, howToPlayDownImg,
                                      (self.width *0.75, self.height * 5 / 8 + 100))
        self.highScoresButton = Button(highScoresUpImg, highScoresDownImg,
                                       (self.width * 0.75, self.height * 6/ 8 + 100))

    def setOtherButtons(self):
        playAgainUpImg = imageCache.get("playagainButtonUp.png")
        playAgainDownImg = imageCache.get("playagainButtonDown.png")
        continueUpImg = imageCache.get("continueButtonUp.png")
        continueDownImg = imageCache.get("continueButtonDown.png")
        backUpImg = imageCache.get("backButtonUp.png")
        backDownImg = imageCache.get("backButtonDown.png")

        self.playAgainButton = Button(playAgainUpImg, playAgainDownImg,
                                      (self.width / 2, self.height / 2))
        self.backButton = Button(backUpImg, backDownImg,
                                 (self.width - 80, self.height - 50))
        self.continueButton = Button(continueUpImg, continueDownImg,
                                     (self.width / 2, self.height * 3 / 4))

    def setModeSelectionButtons(self):
        keyboardUpImg = imageCache.get("keyboardButtonUp.png")
        keyboardDownImg = imageCache.get("keyboardButtonDown.png")
        cameraUpImg = imageCache.get("cameraButtonUp.png")
        cameraDownImg = imageCache.get("cameraButtonDown.png")

        self.keyboardButton = Button(keyboardUpImg, keyboardDownImg,
                                     (self.width / 2, self.height * 3 / 5 - 40))
        self.cameraButton = Button(cameraUpImg, cameraDownImg,
                                   (self.width/2, self.height * 4 / 5 - 60))

    def updateDisplay(self, deltaT):
        # clear screen with background
        self.leafGroup.update(deltaT)

        # hero update & collision detection
        self.heroGroup.update(deltaT, self.wallGroup, self.monsterGroup, self.leafGroup,
                           self.foodGroup, self.stats)

        # update the bad guys
        self.monsterGroup.update(self.hero, self.wallGroup, self.heroGroup, self.graph)

        self.stats.drawStats(self.screen)
        self.screen.blit(self.background, (0, 0))
        self.leafGroup.draw(self.screen)
        self.foodGroup.draw(self.screen)
        self.heroGroup.draw(self.screen)
        self.monsterGroup.draw(self.screen)
        pygame.display.flip()

    def startLoop(self):
        self.stats = GameStatus()
        self.setStartButtons()
        titleImg = imageCache.get("title.png")

        blueMonsterRightImg = imageCache.get("blueMonster_forStart.png")
        blueMonsterLeftImg = imageCache.get("blueMonster_forStartL.png")
        bX, bY = 30, self.height * 0.63
        bPosition = (bX, bY)
        bHeadingRight = True
        deltaBX = 2

        greenMonsterRightImg = imageCache.get("greenMonster_forStartR.png")
        greenMonsterLeftImg = imageCache.get("greenMonster_forStartL.png")
        gX, gY = 300, self.height * 0.8
        gPosition = (gX, gY)
        gHeadingLeft = True
        deltaGX = -3

        while (self.mode == "start"):
            self.clock.tick(30)
            self.screen.fill((0, 0, 0))
            self.screen.blit(titleImg, (5, 5))
            if (bHeadingRight == True):
                self.screen.blit(blueMonsterRightImg, bPosition)
            else:
                self.screen.blit(blueMonsterLeftImg, bPosition)
            if (gHeadingLeft == True):
                self.screen.blit(greenMonsterLeftImg, gPosition)
            else:
                self.screen.blit(greenMonsterRightImg, gPosition)
            self.playGameButton.render(self.screen)
            self.howToPlayButton.render(self.screen)
            self.highScoresButton.render(self.screen)
            bX += deltaBX
            bPosition = (bX, bY)
            if (bX > 300 or bX < 30):
                bHeadingRight = not bHeadingRight
                deltaBX = -deltaBX

            gX += deltaGX
            gPosition = (gX, gY)
            if (gX > 300 or gX < 30):
                gHeadingLeft = not gHeadingLeft
                deltaGX = -deltaGX

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitGame()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.playGameButton.render(self.screen)
                    self.howToPlayButton.render(self.screen)
                    self.highScoresButton.render(self.screen)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.playGameButton.render(self.screen)
                    self.howToPlayButton.render(self.screen)
                    self.highScoresButton.render(self.screen)
                    if self.playGameButton.isOver():
                        self.mode = "modeSelection"
                        break
                    elif self.howToPlayButton.isOver():
                        self.mode = "instruction"
                        break
                    elif self.highScoresButton.isOver():
                        self.mode = "highScores"
                        break
            pygame.display.update()

    def instructionLoop(self):
        self.screen.fill((0,0,0))
        instructionImg = imageCache.get("instruction.png")
        while (self.mode == "instruction"):
            self.clock.tick(24)
            self.screen.blit(instructionImg, (0, 25))
            self.backButton.render(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitGame()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.backButton.render(self.screen)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.backButton.render(self.screen)
                    if self.backButton.isOver():
                        self.mode = "start"
                        break
            pygame.display.update()

    def modeSelectionLoop(self):
        self.screen.fill((0,0,0))
        selectModeImg = imageCache.get("selectMode.png")
        self.screen.blit(selectModeImg, (0, 40))
        while (self.mode == "modeSelection"):
            self.clock.tick(24)
            self.keyboardButton.render(self.screen)
            self.cameraButton.render(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitGame()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.keyboardButton.render(self.screen)
                    self.cameraButton.render(self.screen)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.keyboardButton.render(self.screen)
                    self.cameraButton.render(self.screen)
                    if self.keyboardButton.isOver():
                        self.mode = "keyboard"
                        break
                    elif self.cameraButton.isOver():
                        self.mode = "camera"
                        break
            pygame.display.update()

    def highScoresLoop(self):
        self.readScores("highScores.txt")
        if self.highScores == []:
            self.screen.fill((0,0,0))
            noScoreImg = imageCache.get("noScore.png")
            self.screen.blit(noScoreImg, (0, 0))
        else:
            highscoresImg = imageCache.get("highscores.png")
            self.screen.blit(highscoresImg, (0, 0))
            for i in range(3):
                font = pygame.font.Font("data/Jokerman.ttf", 40)
                text = font.render(self.highScores[i], 1, (128, 64, 0))
                textpos = (self.width * 0.25, self.height * (0.35 + 0.165 * i))
                self.screen.blit(text, textpos)

        while(self.mode == "highScores"):
            self.clock.tick(24)
            self.backButton.render(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitGame()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.backButton.render(self.screen)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.backButton.render(self.screen)
                    if self.backButton.isOver():
                        self.mode = "start"
                        break
            pygame.display.update()

    def pauseLoop(self, cap, mode):
        self.setOtherButtons()
        self.screen.fill((0,0,0))
        pauseImg = imageCache.get("pause.png")
        self.screen.blit(pauseImg, (30, 30))
        while(self.stats.pause == True):
            self.clock.tick(24)
            self.continueButton.render(self.screen)
            self.playAgainButton.render(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitGame()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.continueButton.render(self.screen)
                    self.playAgainButton.render(self.screen)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.continueButton.render(self.screen)
                    self.playAgainButton.render(self.screen)
                    if self.continueButton.isOver():
                        pygame.mouse.set_visible(False)
                        self.stats.pause = False
                    elif self.playAgainButton.isOver():
                        self.stats.pause = False
                        if mode == "camera":
                            cap.release()
                            cv2.destroyAllWindows()
                        self.mode = "start"
            pygame.display.update()

    def keyboardLoop(self):
        pygame.mouse.set_visible(False)
        while (self.stats.pause == False and self.mode == "keyboard"):
            self.loadHero("hero.png")
            while self.stats.lastLevel == False:
                self.stats.nextLevel()
                self.loadLevel("data/levels/level%i" % self.stats.level)
                self.hero.heroMoved = False
                for monster in self.monsterGroup:
                    monster.deltaX = monster.deltaY = 0
                    monster.shortestPath = None

                self.screen.fill((0, 0, 0))

                # only draw animations on background surface
                self.background = pygame.Surface((self.width, self.height - 50)).convert()
                self.background.fill((0, 0, 0))
                # draw map on the backgroud without updating
                self.wallGroup.draw(self.background)
                while self.stats.levelDone == False and self.stats.lives > 0:
                    deltaT = self.clock.tick(24)
                    # handle input
                    for event in pygame.event.get():
                        # handle quit events first
                        if event.type == pygame.QUIT:
                            self.quitGame()

                        # we only want key events for now
                        if not hasattr(event, 'key'): continue
                        if event.key == K_ESCAPE:
                            self.quitGame()
                        if event.key == K_SPACE:
                            self.stats.pause = not self.stats.pause
                            if (self.stats.pause == True):
                                pygame.mouse.set_visible(True)
                                self.pauseLoop(None, "keyboard")
                        if event.key == K_d:
                            self.mode = "end"
                        if (self.mode == "keyboard"):
                            self.hero.handleKeyEvent(event)
                        else:
                            return
                    self.updateDisplay(deltaT)
                if self.stats.lives == 0:
                    self.mode = "end"
                    return
            if self.stats.lastLevel == True and self.stats.levelDone == True:
                self.mode = "win"
                return

    def cameraLoop(self):
        cam_index = 0  # default camera's index is zero.
        cap = cv2.VideoCapture(cam_index)
        cap.open(cam_index)
        pygame.mouse.set_visible(False)
        while (self.stats.pause == False and self.mode == "camera"):
            self.loadHero("hero.png")
            while self.stats.lastLevel == False:
                self.stats.nextLevel()
                self.loadLevel("data/levels/level%i" % self.stats.level)
                self.hero.heroMoved = False
                for monster in self.monsterGroup:
                    monster.deltaX = monster.deltaY = 0
                    monster.shortestPath = None

                self.screen.fill((0, 0, 0))

                # only draw animations on background surface
                self.background = pygame.Surface((self.width, self.height - 50)).convert()
                self.background.fill((0, 0, 0))
                # draw map on the backgroud without updating
                self.wallGroup.draw(self.background)
                while self.stats.levelDone == False and self.stats.lives > 0:
                    deltaT = self.clock.tick(24)
                    motionTrack(cap, self.hero)
                    # handle input
                    for event in pygame.event.get():
                        # handle quit events first
                        if event.type == pygame.QUIT:
                            cap.release()
                            cv2.destroyAllWindows()
                            self.quitGame()

                        # we only want key events for now
                        if not hasattr(event, 'key'): continue
                        if event.key == K_ESCAPE:
                            cap.release()
                            cv2.destroyAllWindows()
                            self.quitGame()
                        if event.key == K_SPACE:
                            self.stats.pause = not self.stats.pause
                            if (self.stats.pause == True):
                                pygame.mouse.set_visible(True)
                                self.pauseLoop(cap, "camera")
                        if event.key == K_d:
                            self.mode = "end"
                        else:
                            return
                    self.updateDisplay(deltaT)
                if self.stats.lives == 0:
                    self.mode = "end"
                    cap.release()
                    cv2.destroyAllWindows()
                    return
            if self.stats.lastLevel == True and self.stats.levelDone == True:
                self.mode = "win"
                cap.release()
                cv2.destroyAllWindows()
                return

    def endLoop(self):
        pygame.mouse.set_visible(True)
        self.writeScores("highScores.txt",self.stats.points)
        self.screen.fill((0,0,0))
        endImg = imageCache.get("end.png")
        self.screen.blit(endImg, (0, 0))
        font = pygame.font.Font("data/Jokerman.ttf", 60)
        text = font.render("%i" % (self.stats.points),1, (255,201,14))
        textpos = (self.width * 0.46, self.height * 0.625)
        self.screen.blit(text, textpos)
        while (self.mode == "end"):
            self.clock.tick(10)
            self.playAgainButton.render(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitGame()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.playAgainButton.render(self.screen)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.playAgainButton.render(self.screen)
                    if self.playAgainButton.isOver():
                        self.mode = "start"
            pygame.display.update()

    def winLoop(self):
        pygame.mouse.set_visible(True)
        self.writeScores("highScores.txt",self.stats.points)
        self.screen.fill((0, 0, 0))
        winImg = imageCache.get("win.png")
        self.screen.blit(winImg, (5,5))
        while (self.mode == "win"):
            self.clock.tick(10)
            self.playAgainButton.render(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitGame()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.playAgainButton.render(self.screen)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.playAgainButton.render(self.screen)
                    if self.playAgainButton.isOver():
                        self.mode = "start"
            pygame.display.update()

    def run(self):
        while(True):
            if (self.mode == "start"):
                self.startLoop()

            if (self.mode == "modeSelection"):
                self.setModeSelectionButtons()
                self.modeSelectionLoop()

            if (self.mode == "keyboard"):
                self.keyboardLoop()

            if (self.mode == "camera"):
                self.cameraLoop()

            if (self.mode != "start"):
                self.setOtherButtons()
                if (self.mode == "instruction"):
                    self.instructionLoop()

                if (self.mode == "highScores"):
                    self.highScoresLoop()

                if (self.mode == "end"):
                    self.endLoop()

                if (self.mode == "win"):
                    self.winLoop()

    def quitGame(self):
        # self.splash = imageCache.get("credits.png")
        # self.screen.blit(self.splash, (0, 0))
        # pygame.display.flip()
        # time.sleep(1)
        self.screen.fill((0,0,0))
        creditImg = imageCache.get("credit.png")
        while(True):
            self.screen.blit(creditImg, (20, 20))
            self.clock.tick(10)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    def loadHero(self, fileName):
        heroImage = imageCache.get(fileName)
        self.hero = HeroSprite(BLOCKSIZE, (0, 0), heroImage)
        self.heroGroup = pygame.sprite.Group(self.hero)

    def loadMonsters(self,monsterType):
        if monsterType == "B":
            bmonsterImgUp = imageCache.get("blueUp.png")
            bmonsterImgLeft = imageCache.get("blueLeft.png")
            bmonsterImgDown = imageCache.get("blueDown.png")
            bmonsterImgRight = imageCache.get("blueRight.png")
            self.blueMonsterFrames = [bmonsterImgUp, bmonsterImgLeft, bmonsterImgDown, bmonsterImgRight]

        if monsterType == "G":
            gmonsterImgUp = imageCache.get("greenUp.png")
            gmonsterImgLeft = imageCache.get("greenLeft.png")
            gmonsterImgDown = imageCache.get("greenDown.png")
            gmonsterImgRight = imageCache.get("greenRight.png")
            self.greenMonsterFrames = [gmonsterImgUp, gmonsterImgLeft, gmonsterImgDown, gmonsterImgRight]

    def loadLevel(self, path):
        self.stats.levelDone = False
        # Create sprite groups
        self.wallGroup = pygame.sprite.Group()
        self.foodGroup = pygame.sprite.Group()
        self.monsterGroup = pygame.sprite.Group()
        self.leafGroup = pygame.sprite.Group()

        # Open level file
        levelFile = open(path)

        # First line is the wall image
        wallImgFilename = levelFile.readline().strip()
        wallImg = imageCache.get(wallImgFilename)

        # 2nd line is number of food types
        numFoodTypes = int(levelFile.readline().strip())
        foodTypes = {}
        # Used for generate graph
        wallList = []

        # next n-lines are food types with key, image, points
        for i in range(numFoodTypes):
            line = levelFile.readline().strip().split(',')
            key = line[0]
            imageName = line[1]
            points = int(line[2])
            if line[3] == "true":
                required = True
            else:
                required = False
            image = imageCache.get(imageName)
            foodTypes[key] = [image, points, required]

        # next line is num monsters
        numMonsters = int(levelFile.readline().strip())
        for i in range(numMonsters):
            line = levelFile.readline().strip().split(',')
            if line[0] == "B":
                self.monsterGroup.add(MonsterSprite(BLOCKSIZE, (int(line[1]), int(line[2])),
                                                    self.blueMonsterFrames, int(line[3]), line[4]))
            elif line[0] == "G":
                self.monsterGroup.add(MonsterSprite(BLOCKSIZE, (int(line[1]), int(line[2])),
                                                    self.greenMonsterFrames, int(line[3]), line[4]))

        # The rest of the lines define the map
        for row in range(NUMSPACES):
            line = levelFile.readline()
            for col in range(NUMSPACES + 5):
                key = line[col]
                if key == "w":
                    self.wallGroup.add(WallSprite((col, row), wallImg))
                    wallList.append((col,row))
                elif key == "S":
                    self.hero.setpos((col, row))
                    self.stats.startPos = (col, row)
                    self.leafGroup.add(LeafSprite((col, row), "blue"))
                elif key == "E":
                    self.leafGroup.add(LeafSprite((col, row), "yellow"))
                elif key in foodTypes.keys():
                    food = foodTypes[key]
                    self.foodGroup.add(
                        FoodSprite((col, row), food[0], food[1], food[2]))

        # read flag to indicate we've reached the last level
        if levelFile.readline().strip() == "last":
            self.stats.lastLevel = True

        self.graph = nx.grid_2d_graph(NUMSPACES + 5, NUMSPACES)
        self.graph.remove_nodes_from(wallList)
        #print list(self.graph.nodes)

if __name__ == "__main__":
    game = FoodRushGame()
    game.run()
