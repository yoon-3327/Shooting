from tkinter import *
import time
import pygame
import random

class Enemy:
    def __init__(self, canvas, images, id):
        self.canvas = canvas
        self.images = images
        self.id = 'e' + str(id)
        self.me = self.canvas.create_image(random.randint(10, 390), 0,
                                           image=self.images[0], tags=self.id)
        self.frame = 0

    def update(self):
        self.canvas.itemconfig(self.me, image=self.images[self.frame % len(self.images)])
        self.canvas.move(self.me, 0, 4)
        self.frame += 1

    def getPos(self):
        return self.canvas.coords(self.me)

    def getId(self):
        return self.me


class ShootingGame:
    def __init__(self):
        self.window = Tk()
        self.window.title("빨간망토")
        self.window.geometry("400x500")
        self.window.resizable(0, 0)
        self.lastTime = time.time()
        self.keys = set()

        self.canvas = Canvas(self.window, bg="white")
        self.canvas.pack(expand=True, fill=BOTH)
        self.window.bind("<KeyPress>", self.keyPressHandler)
        self.window.bind("<KeyRelease>", self.keyReleaseHandler)
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)

        self.myimages = []
        gif = 'image/redhood.gif'
        frame_index = 0
        while True:
            try:
                frame = PhotoImage(file=gif, format=f"gif -index {frame_index}").subsample(3)
                self.myimages.append(frame)
                frame_index += 1
            except:
                break

        self.my_image_number = 0
        self.lastAnim = time.time()

        self.enemyimages = [PhotoImage(file='image/mushroom.gif').subsample(6)]
        self.enemy_img_number = 0

        self.bgimage = PhotoImage(file="image/bgimage2.png")
        self.canvas.create_image(0, 0, image=self.bgimage, anchor=NW, tags="bg")

        self.rock = PhotoImage(file="image/rock.png")
        self.heartimg = PhotoImage(file="image/heart.png").subsample(10)

        self.window.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        self.redhood = self.canvas.create_image(
            canvas_width // 2, canvas_height,
            image=self.myimages[0],
            tags="redhood",
            anchor='s'
        )

        self.hearts = []
        for i in range(3):
            h = self.canvas.create_image(20 + (i * 30), 20,
                                         image=self.heartimg,
                                         anchor='nw',
                                         tags="heart")
            self.hearts.append(h)

        self.score = 0
        self.score_text = self.canvas.create_text(
            380, 20, text="0", fill="white",
            font=("Arial", 16, "bold"), anchor="ne"
        )

        self.enemy_list = []
        self.enemy_id = 0

        pygame.init()
        self.rock_sound = pygame.mixer.Sound("sound/rock.wav")
        self.game_running = False

        self.start_button = Button(self.window, text="Game Start",
                                   font=("Arial", 16, "bold"),
                                   command=self.start_game)
        self.start_button.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.window.mainloop()

    def start_game(self):
        self.game_running = True
        self.start_button.destroy()

        pygame.mixer.music.load("sound/bgm.mp3")
        pygame.mixer.music.play(-1)

        self.game_loop()

    def game_loop(self):
        if not self.game_running:
            return

        try:
            self.checkCrash()

            if time.time() - self.lastAnim > 0.12:
                self.canvas.itemconfig(
                    self.redhood,
                    image=self.myimages[self.my_image_number % len(self.myimages)]
                )
                self.my_image_number += 1
                self.lastAnim = time.time()

            rocks = self.canvas.find_withtag("rock")
            self.display()

            for rock in rocks:
                self.canvas.move(rock, 0, -9)
                if self.canvas.coords(rock)[1] < 0:
                    self.canvas.delete(rock)

            self.manageEnemy()

        except TclError:
            return

        self.window.after(33, self.game_loop)

    def checkCrash(self):
        d_x, d_y = self.canvas.coords(self.redhood)

        for e in list(self.enemy_list):
            e_x, e_y = e.getPos()

            if abs(e_x - d_x) < 80 and abs(e_y - d_y) < 140:
                self.canvas.delete(e.getId())
                self.enemy_list.remove(e)
                self.removeHeart()
                return

    def removeHeart(self):
        if len(self.hearts) > 0:
            last = self.hearts.pop()
            self.canvas.delete(last)

        if len(self.hearts) == 0:
            self.gameOver()

    def missionClear(self):
        self.game_running = False

        self.canvas.create_text(200, 200,
                                text="성공!",
                                fill="yellow",
                                font=("Arial", 32, "bold"))

        exit_button = Button(self.window, text="EXIT",
                             font=("Arial", 16, "bold"),
                             command=self.onClose)
        exit_button.place(relx=0.5, rely=0.6, anchor=CENTER)

    def gameOver(self):
        self.game_running = False
        self.canvas.create_text(200, 250, text="GAME OVER",
                                fill="red",
                                font=("Arial", 32, "bold"),
                                tags="gameover")
        self.window.update()
        time.sleep(2)
        self.onClose()

    def manageEnemy(self):
        if random.randint(0, 70) == 0:
            self.enemy_list.append(Enemy(self.canvas, self.enemyimages, self.enemy_id))
            self.enemy_id += 1

        for e in list(self.enemy_list):
            e.update()
            if e.getPos()[1] > self.canvas.winfo_height():
                self.canvas.delete(e.getId())
                self.enemy_list.remove(e)

        rocks = self.canvas.find_withtag("rock")
        area = 25

        for rock in rocks:
            f_x, f_y = self.canvas.coords(rock)
            for e in list(self.enemy_list):
                e_x, e_y = e.getPos()

                if e_x - area < f_x < e_x + area and e_y - area < f_y < e_y + area:
                    self.canvas.delete(e.getId())
                    self.enemy_list.remove(e)
                    self.canvas.delete(rock)

                    self.score += 1
                    self.canvas.itemconfig(self.score_text, text=str(self.score))

                    if self.score == 25:
                        self.missionClear()
                        return

    def keyReleaseHandler(self, event):
        if event.keycode in self.keys:
            self.keys.remove(event.keycode)

    def display(self):
        redhood = self.canvas.find_withtag("redhood")
        for key in self.keys:
            if key == 39:
                x, y = self.canvas.coords(redhood)
                if x + 5 < self.canvas.winfo_width():
                    self.canvas.move(redhood, 5, 0)

            if key == 37:
                x, y = self.canvas.coords(redhood)
                if x - 5 > 0:
                    self.canvas.move(redhood, -5, 0)

            if key == 32:
                now = time.time()
                if now - self.lastTime > 0.3:
                    self.lastTime = now
                    x, y = self.canvas.coords(redhood)
                    self.canvas.create_image(x, y - 50, image=self.rock, tags="rock")
                    self.rock_sound.play()

    def keyPressHandler(self, event):
        if event.keycode == 27:
            self.onClose()
        else:
            self.keys.add(event.keycode)

    def onClose(self):
        self.game_running = False
        pygame.mixer.music.stop()
        pygame.quit()
        self.window.destroy()

if __name__=='__main__':
    ShootingGame()

