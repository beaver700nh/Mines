from tkinter import *
from tkinter import messagebox
from random import random
from time import sleep

PLAY = 0
DEAD = 1
WIN = 2

DUNNO = 0
FLAGGED = 1
EXPOSED = 2
BOMB = 2

charsetmap = (u"\u2690", u"\u2691", u"\u26a0")
colormap = ("#00c000", "#ff8800", "#ff0000")

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

        self.score_label = Label(self.tk, textvariable=self.score, padx=10, pady=10, font=("Arial", 18))
        self.score_label.place(x=25, y=25)

        self.time = IntVar()
        self.time.set(0)

        self.time_label = Label(self.tk, textvariable=self.time, padx=10, pady=10, font=("Arial", 18))
        self.time_label.place(x=650, y=25)

        self.mode = StringVar()
        self.mode.set("Exposing")

        self.mode_label = Label(self.tk, textvariable=self.mode, padx=10, pady=10, font=("Arial", 18))
        self.mode_label.place(x=425, y=25)

        self.button = Button(self.tk, padx=10, pady=10, text="New Game", font=("Arial", 18), command=self.new_game)
        self.button.place(x=225, y=25)

        self.refresh()

        self.tk.bind_all("<Escape>", self.end)
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

        self.text = StringVar()
        self.text.set(charsetmap[self.state])

        self.square = Button(self.game.tk, padx=23, pady=20, bg="#e7e7e7", fg="#000000", font=("Arial", 18),
                             textvariable=self.text, command=self.callback)
        self.square.place(x=x+1, y=y+101)

    def callback(self):
        if self.game.mode.get() == "Exposing":
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
        self.text.set(charsetmap[self.state])
        self.square.config(fg=colormap[self.state])

        if self.text.get() == charsetmap[BOMB]:
            self.game.state = DEAD

g = Game()

g.grid = [[Square(g, x*75, y*75) for y in range(0, 10)] \
                                 for x in range(0, 10)]

g.mainloop()
