from cv2 import cv2
import pyautogui
import os
import numpy as np
import mss
import time
import sys
## TODO: server overload detection, newmap log, refresh heroes

threshold_connect_wallet = 0.6
threshold_metamask_select = 0.6
threshold_unlock_img = 0.8
threshold_sign_img = 0.8
threshold_error = 0.5
threshold_back = 0.7
threshold_hero_icon = 0.3
threshold_work = 0.7
threshold_tresure = 0.4

hero_work_interval = 30

login_attempts = 0

pyautogui.FAILSAFE = True

## Login image block
connect_wallet_img = cv2.imread('imgs/connect_wallet.png')
metamask_select_img = cv2.imread('imgs/metamask_select.png')
metamask_unlock_img = cv2.imread('imgs/unlock_metamask.png')
metamask_sign_img = cv2.imread('imgs/metamask_sign.png')
metamask_cancel_button = cv2.imread('imgs/metamask_cancel_button.png')
error_img = cv2.imread('imgs/error.png')
error_ok_img = cv2.imread('imgs/error_ok.png')

## Game image block 
treasure_hunt_img = cv2.imread('imgs/treasure_hunt.png')
back_button_img = cv2.imread('imgs/back_button.png')
hero_icon = cv2.imread('imgs/hero_icon.png')
character_indicator = cv2.imread('imgs/character_indicator.png')
character_close_button = cv2.imread('imgs/character_close_button.png')
work_rest = cv2.imread('imgs/work_rest.png')
new_map = cv2.imread('imgs/new_map.png')


def printScreen():
    with mss.mss() as sct:
        monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}
        sct_img = np.array(sct.grab(sct.monitors[0]))
        return sct_img[:,:,:3]


def get_coord(target, threshold):
    img = printScreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    if len(rectangles) > 0:
        return rectangles
    else:
        return False

def click_btn(coordinates):
    x,y,w,h = coordinates[0]
    pyautogui.moveTo(x+w/2,y+h/2,1)
    pyautogui.click()


def login():
    global login_attempts

    connect_wallet_coord = get_coord(connect_wallet_img, threshold_connect_wallet)
    if connect_wallet_coord is not False:
        sys.stdout.write("\nFound login button.")
        click_btn(connect_wallet_coord)
        time.sleep(3)

    metamask_select_coord = get_coord(metamask_select_img, threshold_metamask_select)
    if metamask_select_coord is not False:
        sys.stdout.write("\nFound metamask button.")
        click_btn(metamask_select_coord)
        time.sleep(5)
    

    metamask_unlock_coord = get_coord(metamask_unlock_img, threshold_unlock_img)
    if metamask_unlock_coord is not False:
        sys.stdout.write("\nFound unlock button. Delaying in case of bad bsc connection.")
        time.sleep(5)
        click_btn(metamask_unlock_coord)
        time.sleep(5)
    else:
        sys.stdout.write("\nDidn't found unlock button. Wallet probably already unlocked.")

    time.sleep(3)

    sign_button_coord = get_coord(metamask_sign_img, threshold_sign_img)
    if sign_button_coord is not False:  
        click_btn(sign_button_coord)
        login_attempts = 0
        time.sleep(15)
        if current_screen() == "main":
            sys.stdout.write("\nLogged in.")
            return True
        else:
            time.sleep(10)
            login()
    else:
        sys.stdout.write("\nLogin failed. Trying again.")
        login_attempts += 1
        if (login_attempts > 3):
            sys.stdout.write("\n>3 login attemps. Retrying.")
            pyautogui.hotkey('ctrl', 'f5')
            login_attempts = 0
            cancel_button_coord = get_coord(metamask_cancel_button, threshold_unlock_img)
            if cancel_button_coord is not False:
                sys.stdout.write("\nMetamask is glitched. Cancelling and restarting")
                click_btn(cancel_button_coord)
            time.sleep(8)
        login()

def handle_error():
    click_btn(get_coord(error_ok_img, threshold_connect_wallet)) 
    pyautogui.hotkey('ctrl', 'f5')
    time.sleep(8)
    login()



def current_screen():
    if get_coord(back_button_img, threshold_back) is not False:
        return "thunt"
    elif get_coord(treasure_hunt_img, threshold_connect_wallet) is not False:
        return "main"
    elif get_coord(connect_wallet_img, threshold_connect_wallet) is not False:
        return "login"
    elif get_coord(character_indicator, threshold_error) is not False:
        return "character"
    else:
        return "unknown"
    

def heroes_work():
    screen = current_screen()
    sys.stdout.write("\nSending heroes to work!")
    if screen == "thunt":
        click_btn(get_coord(back_button_img, threshold_back))
        time.sleep(2)
        screen = current_screen()
    if screen == "main":
        hero_icon_coord = get_coord(hero_icon, threshold_hero_icon)
        if hero_icon_coord is not False:
            click_btn(hero_icon_coord)
            time.sleep(5)
            screen = current_screen()
    if screen == "character":
        sys.stdout.write("\nCharacter screen!")

        width, height = pyautogui.size()
        pyautogui.moveTo(width/2, height/2)
        pyautogui.scroll(-100)

        work_button_list = get_coord(work_rest, threshold_work)
        while work_button_list is not False:
            x,y,w,h = work_button_list[-1]
            pyautogui.moveTo(x-10+w/2,y+h/2,1)
            pyautogui.click()
            ## Check overload
            work_button_list = get_coord(work_rest, threshold_work)
            time.sleep(4)
        click_btn(get_coord(character_close_button, threshold_back))
        sys.stdout.write("\nFinished putting to work.")
    

def main():
    last = {
    "heroes_work" : 0,
    "new_map" : 0,
    "refresh_heroes" : 0
    }

    while True:
        screen = current_screen()
        sys.stdout.write("\nCurrent screen:" + screen)
        ## Check for login screen
        if screen == "login":
            login()
            time.sleep(5)
        
        ## Check for error button.
        error_coord = get_coord(error_img, threshold_error)
        if error_coord is not False:
            sys.stdout.write("\nError detected. Trying to resolve.")
            handle_error()
        else:
            sys.stdout.write("\nNo error detected. Continuing")


        now = time.time()
        if now - last["heroes_work"] > hero_work_interval * 60: ## Check to see if heroes have been sent to work in the last n minutes
            heroes_work()
            last["heroes_work"] = now ## Update latest time
            time.sleep(3)
        
        screen = current_screen()

        if screen == "main":
            click_btn(get_coord(treasure_hunt_img, threshold_tresure))
            
        if screen == "thunt":
            newmap_coord = get_coord(new_map, threshold_connect_wallet)
            if newmap_coord is not False:
                click_btn(newmap_coord)

        time.sleep(60)


main()