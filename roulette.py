import numpy as np
import cv2 as cv
from PIL import ImageGrab

import pyautogui
import csv

import time
from random import randint


class Play:
    def __init__(self, mode, bet, clicks):
        self.mode = mode  # modes: red/black, even/odd, 1_18/19_36, random b/r, numbers
        self.default_modes = ["red", "black", "even", "odd", "1_18", "19_36"]
        self.coordinates = {
            "black": {
                "x": 535,
                "y": 700
            },
            "red": {
                "x": 420,
                "y": 702
            },
            "odd": {
                "x": 664,
                "y": 699
            },
            "even": {
                "x": 290,
                "y": 697
            },
            "numbers": {
                "table": {
                    "x": 75,
                    "y": 767
                },
                "neighbors": {
                    "x": 163,
                    "y": 429
                },
                "one": {
                    "x": 159,
                    "y": 624
                }
            },
            "1_18": {
                "x": 167,
                "y": 701
            },
            "19_36": {
                "x": 778,
                "y": 701
            }
        }

        self.bet = bet
        self.default_bet = bet
        self.clicks = clicks

        self.loses = 0
        self.max_loses = 0
        self.deposit = self.read_last_dep()
        # IMG you won
        img = cv.imread("screens/you_won.png")
        self.you_won = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # IMG LOSES
        self.img_loses = []
        img = cv.imread("screens/you_lose_red.png")
        self.img_loses.append(cv.cvtColor(img, cv.COLOR_BGR2GRAY))
        img = cv.imread("screens/you_lose_black.png")
        self.img_loses.append(cv.cvtColor(img, cv.COLOR_BGR2GRAY))
        img = cv.imread("screens/you_lose_zero.png")
        self.img_loses.append(cv.cvtColor(img, cv.COLOR_BGR2GRAY))

        # IMG Play for fun
        img = cv.imread("screens/you_await.png")
        self.you_await = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    @staticmethod
    def read_last_dep():
        with open('deposit.txt', 'r') as file:
            dep = float(file.read())
        return dep

    def default_params(self):
        self.loses = 0
        self.bet = self.default_bet

    def write_date(self, res):
        local_dep = round(self.deposit, 2)

        with open(f'_data/data_{time.strftime("%d", time.localtime())}.csv', mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([time.strftime("%H:%M:%S", time.localtime()), local_dep, res])

        with open('deposit.txt', 'w') as file:
            file.write(str(local_dep))

    def write_max_loses(self):
        self.max_loses += 1
        with open('max_loses.txt', mode='w') as txt:
            txt.write(f"{self.max_loses}")

    def check_win_or_lose(self):
        img = ImageGrab.grab(bbox=(0, 0, 960, 1079))
        img_np = np.array(img)
        cv_img = cv.cvtColor(img_np, cv.COLOR_BGR2GRAY)  # COLOR_BGR2RGB

        res = cv.matchTemplate(cv_img, self.you_won, cv.TM_CCOEFF_NORMED)
        loc = np.where(res >= .9)
        for _ in zip(*loc[::-1]):
            return "won"

        for template_img in self.img_loses:
            res = cv.matchTemplate(cv_img, template_img, cv.TM_CCOEFF_NORMED)
            loc = np.where(res >= .8)
            for _ in zip(*loc[::-1]):
                return "lose"

    def check_pff(self):
        checking_time_pff = time.monotonic() + 1.50
        while time.monotonic() < checking_time_pff:
            img = ImageGrab.grab(bbox=(0, 0, 960, 1079))
            img_np = np.array(img)
            img_rgb = cv.cvtColor(img_np, cv.COLOR_BGR2GRAY)

            res = cv.matchTemplate(img_rgb, self.you_await, cv.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.9)
            for _ in zip(*loc[::-1]):
                pyautogui.click(498, 655, duration=.5)
                print("close await screen")
                break
            time.sleep(.1)

    def playing(self):
        print(f"==== start bot, mode: {self.mode} ====")

        number = 1  # setting for reverse mode
        while True:
            # if self.loses > 9 or (self.mode == "numbers" and self.loses == 7):
            #     print("So much loses")
            #     return

            # check screen "playing for fun"
            self.check_pff()

            # refactor this code to more useful use for another strategy
            # settings for bets
            if self.mode == "numbers":
                # open "table"
                _x = self.coordinates[self.mode]["table"]["x"]
                _y = self.coordinates[self.mode]["table"]["y"]
                pyautogui.moveTo(_x, _y, duration=.5)
                pyautogui.click()
                # make bet on 17 numbers

                _x = self.coordinates[self.mode]["neighbors"]["x"]
                _y = self.coordinates[self.mode]["neighbors"]["y"]
                pyautogui.moveTo(_x, _y, duration=.5)
                pyautogui.click()

                # make bet on 1 number

                _x = self.coordinates[self.mode]["one"]["x"]
                _y = self.coordinates[self.mode]["one"]["y"]
                pyautogui.moveTo(_x, _y, duration=.5)
                pyautogui.click()
            # random on black or red
            if self.mode == "random":
                rand = randint(1, 2)
                if rand == 1:
                    _x = self.coordinates["red"]["x"]
                    _y = self.coordinates["red"]["y"]
                    pyautogui.moveTo(_x, _y, duration=.5)
                    pyautogui.click()
                elif rand == 2:
                    _x = self.coordinates["black"]["x"]
                    _y = self.coordinates["black"]["y"]
                    pyautogui.moveTo(_x, _y, duration=.5)
                    pyautogui.click()
            # first red second black
            if self.mode == "reverse":
                if number % 2 == 0:
                    select = "1_18"
                else:
                    select = "19_36"
                _x = self.coordinates[select]["x"]
                _y = self.coordinates[select]["y"]
                pyautogui.moveTo(_x, _y, duration=.5)
                pyautogui.click()
                number += 1
            # default bets Martingale
            if self.mode in self.default_modes:
                _x = self.coordinates[self.mode]["x"]
                _y = self.coordinates[self.mode]["y"]
                pyautogui.moveTo(_x, _y, duration=.5)
                pyautogui.click(clicks=self.clicks)

            # make x2
            if self.loses != 0:
                pyautogui.click(741, 763, clicks=self.loses, duration=.3)

            self.deposit -= self.bet

            if self.deposit < 0:
                print("you all lose")
                return

            # start roulette
            pyautogui.moveTo(914, 762, duration=.2)
            pyautogui.click()

            # check 4 seconds win or lose
            time.sleep(.5)
            checking_time = time.monotonic() + 5
            while time.monotonic() < checking_time:
                result = self.check_win_or_lose()
                if result is "won":
                    win_bet = round(self.bet * 2, 2)
                    self.deposit += win_bet
                    self.write_date("win")
                    self.default_params()
                    print(f"You won {win_bet}")
                    break
                elif result is "lose":
                    print(f"You lose {self.bet}")
                    self.write_date("lose")
                    self.bet *= 2
                    self.loses += 1
                    if self.loses > self.max_loses:
                        self.write_max_loses()
                    break

            time.sleep(2)

if __name__ == "__main__":
    roulette = Play("reverse", bet=.1, clicks=1)
    roulette.playing()
