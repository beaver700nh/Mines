from tkinter import *
from tkinter import messagebox
from random import randrange
from time import sleep

PLAY = 0
DEAD = 1
WIN = 2

DUNNO = 0
FLAGGED = 1
EXPOSED = 2

EMPTY = 0
NUMBER = 1
MINE = 2

RED = "#ff0000"
ORANGE = "#ff8800"
GREEN = "#00c000"
LIGHT_GRAY = "#e7e7e7"
BLACK = "#000000"

MYFONT = ("Courier", 18)

colormap = [GREEN, ORANGE]

class Game:
    def __init__(self):
        self.tk = Tk()
        self.tk.title("Minesweeper")
        self.tk.resizable(0, 0)
        self.tk.wm_attributes("-topmost", 1)

        temp_x = int(self.tk.winfo_screenwidth() / 2 - 375)
        temp_y = int(self.tk.winfo_screenheight() / 2 - 425)

        self.tk.geometry("750x850+{0}+{1}".format(temp_x, temp_y))

        self.state = PLAY
        self.grid = []
        self.remaining = 25

        self.score = StringVar()
        self.score.set("00 / 25")

        self.score_label = Label(self.tk, textvariable=self.score, padx=10, pady=10, font=MYFONT)
        self.score_label.grid(row=0, column=0)

        self.time = IntVar()
        self.time.set(0)

        self.time_label = Label(self.tk, textvariable=self.time, padx=10, pady=10, font=MYFONT)
        self.time_label.grid(row=0, column=8)

        self.mode = StringVar()
        self.mode.set("Exposing")

        self.mode_label = Label(self.tk, textvariable=self.mode, padx=10, pady=10, font=MYFONT)
        self.mode_label.grid(row=0, column=5)

        self.button = Button(self.tk, padx=10, pady=10, text="New Game", font=MYFONT, command=self.new_game)
        self.button.grid(row=0, column=2)

        self.flagged_image = PhotoImage(file="./images/flagged.gif")
        self.dunno_image = PhotoImage(file="./images/dunno.gif")
        self.blank_image = PhotoImage(file="./images/blank.gif")
        self.mine_image = PhotoImage(file="./images/mine.gif")
        self.number_image = [PhotoImage(file="./images/number{0}.gif".format(i)) for i in range(1, 9)]

        ## access using self.grid[x][y] where 0 < x < 10 and 0 < y < 10

        self.grid = [[Square(self, x+1, y) for y in range(0, 10)] \
                                           for x in range(0, 10)]

        for i in range(0, 25):
            random_square = self.grid[randrange(0, 10)][randrange(0, 10)]

            while random_square.type != EMPTY:
                random_square = self.grid[randrange(0, 10)][randrange(0, 10)]
                
            random_square.type = MINE

        self.refresh()

        self.tk.bind_all("q", self.end)
        self.tk.bind_all("<question>", self.info)
        self.tk.bind_all("m", self.toggle_mode)

        self.tk.after(1000, self.tick)

    def end(self, *ignore):
        if messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.tk.destroy()

    def info(self, *ignore):
        messagebox.showinfo("Help", "In flagging mode, click once to flag, again to unflag.\n" \
                                    "In exposing mode, click once to expose." \
                                    "To change modes, type \"m\"." \
                                    "Type ? for help. Type ESC to quit the game.")

    def toggle_mode(self, *ignore):
        if self.mode.get() == "Exposing":
            self.mode.set("Flagging")

        elif self.mode.get() == "Flagging":
            self.mode.set("Exposing")

    def tick(self):
        self.time.set(self.time.get() + 1)

        self.tk.after(1000, self.tick)

    def new_game(self):
        self.time.set(0)
        self.mode.set("Exposing")
        self.remaining = 25
        
        for column in self.grid:
            for square in column:
                square.state = DUNNO
                square.flagged = False

    def refresh(self):
        self.tk.update()
        self.tk.update_idletasks()

    def mainloop(self):
        while self.state == PLAY:
            for column in self.grid:
                for square in column:
                    square.animate()

            self.score.set("{0:02} / 25".format(25 - self.remaining))

            self.refresh()
            sleep(0.01)

        if self.state == DEAD:
            messagebox.showinfo("You Lost", "You lost. Better luck next time!")

        elif self.state == WIN:
            messagebox.showinfo("You Won", "You won! Very nice job!")

class Square:
    def __init__(self, game, x, y):
        self.game = game

        self.state = DUNNO
        self.flagged = False
        self.type = EMPTY

        self.square = Button(self.game.tk, bg=LIGHT_GRAY, fg=BLACK, font=MYFONT,
                             image=self.game.dunno_image, command=self.callback)
        self.square.grid(row=x, column=y)

        self.bombs_around_me = 0

        squares_to_check = [(x-1, y-0), (x-1, y-1), (x-0, y-1), (x+1, y-1), \
                            (x+1, y+0), (x+1, y+1), (x+0, y+1), (x-1, y+1)]

        for x_other, y_other in squares_to_check:
            try:
                if self.game.grid[x_other][y_other].type == MINE:
                    self.bombs_around_me += 1

            except IndexError:
                pass

        if self.bombs_around_me != 0:
            self.type = NUMBER

    def callback(self):
        if self.game.mode.get() == "Exposing" and not self.flagged:
            self.state = EXPOSED

        elif self.game.mode.get() == "Flagging":
            if self.flagged:
                self.state = DUNNO
                self.game.remaining += 1
                self.flagged = False

            elif not self.flagged:
                self.state = FLAGGED
                self.game.remaining -= 1
                self.flagged = True

    def animate(self):
        if self.state == EXPOSED:
            if self.type == MINE:
                self.square.config(image=self.game.mine_image)
                self.game.state = DEAD

            elif self.type == EMPTY:
                self.square.config(image=self.game.blank_image)

            elif self.type == NUMBER:
                self.square.config(image=self.game.number_image[self.bombs_around_me])

        elif self.state == FLAGGED:
            self.square.config(image=self.game.flagged_image)

        else:
            self.square.config(image=self.game.dunno_image)

g = Game()

g.mainloop()
