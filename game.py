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

        self.state = PLAY
        self.board = []
        self.remaining = 25

        self.score = StringVar()
        self.score.set("00 / 25")

        self.score_label = Label(self.tk, textvariable=self.score, padx=10, pady=10, font=MYFONT)
        self.score_label.grid(row=0, column=0, columnspan=3, sticky=N+E+W+S)

        self.time = IntVar()
        self.time.set(0)

        self.time_label = Label(self.tk, textvariable=self.time, padx=10, pady=10, font=MYFONT)
        self.time_label.grid(row=0, column=7, columnspan=3, sticky=N+E+W+S)

        self.button = Button(self.tk, padx=10, pady=10, text="New Game", font=MYFONT, command=self.new_game)
        self.button.grid(row=0, column=3, columnspan=4, sticky=N+E+W+S)

        temp_x = self.tk.winfo_screenwidth() // 2 - 375
        temp_y = self.tk.winfo_screenheight() // 2 - 425

        self.tk.geometry("+{0}+{1}".format(temp_x, temp_y))

        self.flagged_image = PhotoImage(file="./Images/flagged.gif")
        self.dunno_image = PhotoImage(file="./Images/dunno.gif")
        self.blank_image = PhotoImage(file="./Images/blank.gif")
        self.mine_image = PhotoImage(file="./Images/mine.gif")
        self.number_image = [PhotoImage(file="./Images/number{0}.gif".format(i)) for i in range(1, 9)]

        ## access using self.board[row][col] where 0 < row < 10 and 0 < col < 10

        self.board = [[Tile(self, col+1, row) for row in range(0, 5)] \
                                              for col in range(0, 5)]

        for i in range(0, 5):
            random_tile = self.board[randrange(0, 5)][randrange(0, 5)]

            while random_tile.type != EMPTY:
                random_tile = self.board[randrange(0, 5)][randrange(0, 5)]

            random_tile.type = MINE

        for row in self.board:
            for tile in row:
                tile.check_neighbors()

        for row in self.board:
            for tile in row:
                if tile.type == MINE:
                    print("o", end=" ")

                elif tile.type == NUMBER:
                    print("#", end=" ")

                elif tile.type == EMPTY:
                    print("-", end=" ")

            print("\n")

        self.refresh()

        self.tk.bind_all("q", self.end)
        self.tk.bind_all("<question>", self.info)

        self.tk.after(1000, self.tick)

    def end(self, *ignore):
        if messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.tk.destroy()

    def info(self, *ignore):
        messagebox.showinfo("Help", "Right-click a tile to flag, again to unflag.\n" \
                                    "Left-click a tile once to expose.\n" \
                                    "Type ? for help. Type q to quit the game.")

    def tick(self):
        self.time.set(self.time.get() + 1)

        self.tk.after(1000, self.tick)

    def new_game(self):
        self.time.set(0)
        self.remaining = 25

        for row in self.board:
            for tile in row:
                tile.state = DUNNO
                tile.flagged = False
                tile.tile.config(relief=RAISED)

    def refresh(self):
        self.tk.update()
        self.tk.update_idletasks()

    def mainloop(self):
        while self.state == PLAY:
            for row in self.board:
                for tile in row:
                    tile.animate()

            self.score.set("{0:02} / 25".format(25 - self.remaining))

            self.refresh()
            sleep(0.01)

        if self.state == DEAD:
            messagebox.showinfo("You Lost", "You lost. Better luck next time!")

        elif self.state == WIN:
            messagebox.showinfo("You Won", "You won! Very nice job!")

class Tile:
    def __init__(self, game, col, row):
        self.game = game

        self.state = DUNNO
        self.flagged = False
        self.type = EMPTY

        self._location = (row, col)

        self.tile = Label(self.game.tk, bg=LIGHT_GRAY, fg=BLACK, font=MYFONT, relief=RAISED,
                          width=60, height=60, image=self.game.dunno_image)
        self.tile.grid(row=row, column=col)

        self.mines_around_me = 0

        self.neighbors = [(row-0, col-1), (row-1, col-1), (row-1, col-0), (row-1, col+1), \
                          (row+0, col+1), (row+1, col+1), (row+1, col+0), (row+1, col-1)]

        self.tile.bind("<Button-1>", self.expose)
        self.tile.bind("<Button-3>", self.flag)

    def check_neighbors(self):
        print("Checking tile at row: {0[0]}, col: {0[1]}".format(self._location))

        if self.type == MINE:
            return

        for neighbor_row, neighbor_col in self.neighbors:
            try:
                if self.game.board[neighbor_row][neighbor_col].type == MINE:
                    self.mines_around_me += 1
                    print("Found mine at row: {0}, col: {1}".format(neighbor_row, neighbor_col))

            except IndexError:
                pass

        if self.mines_around_me != 0:
            self.type = NUMBER

        print("Found {0} mines total\n".format(self.mines_around_me))

    def expose(self, *ignore):
        if not self.flagged:
            self.state = EXPOSED
            self.tile.config(relief=FLAT)

    def flag(self, *ignore):
        if self.flagged:
            self.state = DUNNO
            self.game.remaining += 1
            self.flagged = False

        elif self.game.remaining > 0 and not self.flagged:
            self.state = FLAGGED
            self.game.remaining -= 1
            self.flagged = True

    def animate(self):
        if self.state == EXPOSED:
            if self.type == MINE:
                self.tile.config(image=self.game.mine_image)
                self.game.state = DEAD

            elif self.type == EMPTY:
                self.tile.config(image=self.game.blank_image)

            elif self.type == NUMBER:
                self.tile.config(image=self.game.number_image[self.mines_around_me])

        elif self.state == FLAGGED:
            self.tile.config(image=self.game.flagged_image)

        else:
            self.tile.config(image=self.game.dunno_image)

g = Game()

g.mainloop()
