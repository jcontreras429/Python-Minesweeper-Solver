import tkinter, configparser, os, tkinter.messagebox, tkinter.simpledialog
import numpy as np
from random import randint

window = tkinter.Tk()

window.title("Minesweeper")

# Prepare default values

rows = 10
cols = 10
mines = 10
clicks = 0

field = [] # This is the mine field
buttons = [] # Array of buttons
plays = [] # All the current plays so far

colors = ['#FFFFFF', '#0000FF', '#008200', '#FF0000', '#000084', '#840000', '#008284', '#840084', '#000000']

gameover = False
customsizes = []


def createMenu():
    global plays
    menubar = tkinter.Menu(window)
    menusize = tkinter.Menu(window, tearoff=0)
    menusize.add_command(label="Small (10x10 with 10 mines)", command=lambda: setSize(10, 10, 10))
    menusize.add_command(label="Medium (20x20 with 40 mines)", command=lambda: setSize(20, 20, 40))
    menusize.add_command(label="Large (25x50 with 200 mines)", command=lambda: setSize(25, 50, 200))
    menusize.add_command(label="custom", command=setCustomSize)
    menubar.add_cascade(label="Size", menu=menusize)
    menubar.add_command(label="Exit", command=lambda: window.destroy())
    #menubar.add_command(label="Step", command=lambda: nextMove(plays))
    menubar.add_command(label="Solve", command=lambda: solve(plays))
    menubar.add_command(label="Cheat", command=lambda: gridView(field))
    menubar.add_command(label="Count", command=lambda: countMines(field))
    window.config(menu=menubar)
    print("Menu created")


def setCustomSize():
    global customsizes
    r = tkinter.simpledialog.askinteger("Custom size", "Enter amount of rows")
    c = tkinter.simpledialog.askinteger("Custom size", "Enter amount of columns")
    m = tkinter.simpledialog.askinteger("Custom size", "Enter amount of mines")
    while m > r*c:
        m = tkinter.simpledialog.askinteger("Custom size", "Maximum mines for this dimension is: " + str(r*c) + "\nEnter amount of mines")
    customsizes.insert(0, (r,c,m))
    customsizes = customsizes[0:5]
    setSize(r,c,m)
    createMenu()
    #restartGame()

def setSize(r,c,m):
    global rows, cols, mines
    rows = r
    cols = c
    mines = m
    saveConfig()
    restartGame()

def saveConfig():
    global rows, cols, mines, clicks
    clicks = 0
    #configuration
    config = configparser.ConfigParser()
    config.add_section("game")
    config.set("game", "rows", str(rows))
    config.set("game", "cols", str(cols))
    config.set("game", "mines", str(mines))
    config.add_section("sizes")
    config.set("sizes", "amount", str(min(5,len(customsizes))))
    for x in range(0,min(5,len(customsizes))):
        config.set("sizes", "row"+str(x), str(customsizes[x][0]))
        config.set("sizes", "cols"+str(x), str(customsizes[x][1]))
        config.set("sizes", "mines"+str(x), str(customsizes[x][2]))

    with open("config.ini", "w") as file:
        config.write(file)

def loadConfig():
    global rows, cols, mines, customsizes, clicks
    clicks = 0
    config = configparser.ConfigParser()
    config.read("config.ini")
    rows = config.getint("game", "rows")
    cols = config.getint("game", "cols")
    mines = config.getint("game", "mines")
    amountofsizes = config.getint("sizes", "amount")
    for x in range(0, amountofsizes):
        customsizes.append((config.getint("sizes", "row"+str(x)),
                            config.getint("sizes", "cols"+str(x)), config.getint("sizes", "mines"+str(x))))


def startGame():
    global field, clicks
    clicks = 0
    for x in range(0, rows):
        field.append([])
        plays.append([])
        for y in range(0, cols):
            field[x].append(0)
            plays[x].append(0)
    


def prepareGame(v):
    global rows, cols, mines, field, clicks, buttons
    clicks += 1
    L = get_neighbors(v)
    # Generate mines
    for _ in range(mines):
        x = randint(0, rows-1)
        y = randint(0, cols-1)
        # Prevent spawning mine on top of each other
        while (x,y) == v or (x,y) in L or buttons[x][y]['state'] == 'disabled' or field[x][y] == -1:
            x = randint(0, rows-1)
            y = randint(0, cols-1)   
        # This is where we calculate how many mines are next to a tile
        field[x][y] = -1
        if x != 0:
            if y != 0:
                if field[x-1][y-1] != -1:
                    field[x-1][y-1] = int(field[x-1][y-1]) + 1
            if field[x-1][y] != -1:
                field[x-1][y] = int(field[x-1][y]) + 1
            if y != cols-1:
                if field[x-1][y+1] != -1:
                    field[x-1][y+1] = int(field[x-1][y+1]) + 1
        if y != 0:
            if field[x][y-1] != -1:
                field[x][y-1] = int(field[x][y-1]) + 1
        if y != cols-1:
            if field[x][y+1] != -1:
                field[x][y+1] = int(field[x][y+1]) + 1
        if x != rows-1:
            if y != 0:
                if field[x+1][y-1] != -1:
                    field[x+1][y-1] = int(field[x+1][y-1]) + 1
            if field[x+1][y] != -1:
                field[x+1][y] = int(field[x+1][y]) + 1
            if y != cols-1:
                if field[x+1][y+1] != -1:
                    field[x+1][y+1] = int(field[x+1][y+1]) + 1

def prepareWindow():
    global rows, cols, buttons, clicks
    clicks = 0
    tkinter.Button(window, text="Restart", command=restartGame).grid(row=0, column=0, columnspan=cols, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
    buttons = []
    for x in range(rows):
        buttons.append([])
        for y in range(cols):
            b = tkinter.Button(window, text=" ", width=2, command=lambda x=x,y=y: clickOn(x,y))
            b.bind("<Button-3>", lambda e, x=x, y=y:onRightClick(x, y))
            b.grid(row=x+1, column=y, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
            buttons[x].append(b)

def restartGame():
    global gameover, plays, clicks, field
    gameover = False
    clicks = 0
    plays = []
    field = []
    # Destroy all - prevent memory leak
    for x in window.winfo_children():
        if type(x) != tkinter.Menu:
            x.destroy()
    prepareWindow()
    startGame()


def clickOn(x,y):
    global field, buttons, colors, gameover, rows, cols, clicks
    if gameover:
        return
    if clicks == 0:
        prepareGame((x,y))
    buttons[x][y]["text"] = str(field[x][y])
    plays[x][y] = field[x][y]
    if field[x][y] == -1:
        buttons[x][y]["text"] = "*"
        buttons[x][y].config(background='red', disabledforeground='black')
        gameover = True
        tkinter.messagebox.showinfo("Game Over", "You have lost.")
        # Now show all other mines
        for _x in range(0, rows):
            for _y in range(cols):
                if field[_x][_y] == -1:
                    buttons[_x][_y]["text"] = "*"
    else:
        buttons[x][y].config(disabledforeground=colors[field[x][y]])
    if field[x][y] == 0:
        buttons[x][y]["text"] = " "
        # Now repeat for all buttons nearby which are 0... kek
        if clicks != 0:
            autoClickOn(x,y)
        plays[x][y] = 'x'
    buttons[x][y]['state'] = 'disabled'
    buttons[x][y].config(relief=tkinter.SUNKEN)
    checkWin()
    print((x,y),"has been clicked on")

def autoClickOn(x,y):
    global field, buttons, colors, rows, cols
    if buttons[x][y]["state"] == "disabled":
        return
    if field[x][y] != 0:
        buttons[x][y]["text"] = str(field[x][y])
        plays[x][y] = field[x][y]
    else:
        buttons[x][y]["text"] = " "
        plays[x][y] = 'x'
        #print((x,y), "just got auto-clicked")
    buttons[x][y].config(disabledforeground=colors[field[x][y]])
    buttons[x][y].config(relief=tkinter.SUNKEN)
    buttons[x][y]['state'] = 'disabled'
    if field[x][y] == 0:
        if x != 0 and y != 0:
            autoClickOn(x-1,y-1)
        if x != 0:
            autoClickOn(x-1,y)
        if x != 0 and y != cols-1:
            autoClickOn(x-1,y+1)
        if y != 0:
            autoClickOn(x,y-1)
        if y != cols-1:
            autoClickOn(x,y+1)
        if x != rows-1 and y != 0:
            autoClickOn(x+1,y-1)
        if x != rows-1:
            autoClickOn(x+1,y)
        if x != rows-1 and y != cols-1:
            autoClickOn(x+1,y+1)

def onRightClick(x,y):
    global buttons, plays
    if gameover:
        return
    if buttons[x][y]["text"] == "?":
        buttons[x][y]["text"] = " "
        buttons[x][y]["state"] = "normal"
        plays[x][y] = '0'
    elif buttons[x][y]["text"] == " " and buttons[x][y]["state"] == "normal":
        buttons[x][y]["text"] = "?"
        buttons[x][y]["state"] = "disabled"
        plays[x][y] = '?'
    print((x,y), "has been right-clicked")

def checkWin():
    global buttons, field, rows, cols
    win = True
    for x in range(rows):
        for y in range(cols):
            if field[x][y] != -1 and buttons[x][y]["state"] == "normal":
                win = False
    if win:
        tkinter.messagebox.showinfo("Gave Over", "You have won.")
    print("Win check")

if os.path.exists("config.ini"):
    loadConfig()
else:
    saveConfig()


def nextMove(plays):
    global rows, cols
    for r in range(rows):
        for c in range(cols):
            v = (r,c)
            L = get_neighbors(v)
            bombs = 0
            zeros = 0
            if plays[r][c] == 0:
                pass
            elif plays[r][c] in [1,2,3,4,5,6,7,8]:
                num = plays[r][c]
                for x in L:
                    if plays[x[0]][x[1]] == '?':
                        bombs += 1
                    elif plays[x[0]][x[1]] == 0:
                        zeros += 1
                if zeros == 1 and bombs == (num-1):
                    for x in L:
                        if plays[x[0]][x[1]] == 0:
                            onRightClick(x[0], x[1])
                if zeros == num and bombs == 0:
                    for x in L:
                        if plays[x[0]][x[1]] == 0:
                            onRightClick(x[0], x[1])
                if bombs == num:
                    for x in L:
                        if plays[x[0]][x[1]] == 0:
                            clickOn(x[0], x[1])
            
                        

def solve(plays):
        global gameover, clicks, rows, cols
        if clicks == 0:
            r = randint(0, rows-1)
            c = randint(0, cols-1)
            clickOn(r,c)
        counter = 0
        while gameover != True:
            nextMove(plays)
            counter += 1
            if counter > 50:
                return

def gridView(field):
    print(np.matrix(field))

def get_neighbors(v):
    global plays, rows, cols
    r,c = v
    N = [(r+1,c), (r-1,c), (r,c+1), (r,c-1), (r+1,c-1), (r+1,c+1), (r-1,c-1), (r-1,c+1)]
    return [(a,b) for a,b in N if 0<=a<rows and 0<=b<cols]

def countMines(field):
    global rows, cols
    counter = 0
    for r in range(rows):
        for c in range(cols):
            if field[r][c] == -1:
                counter += 1
    print("Bombs:",counter)


createMenu()
prepareWindow()
startGame()
window.mainloop()


