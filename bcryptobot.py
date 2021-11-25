from cv2 import cv2
import pyautogui
import os
import numpy as np
import mss
import time
import sys

## TODO: cleanup, add get_to_place function, add refresh page every x minutes, better login error process

## Higher = bot needs to have more confidence to click it
threshold_connect_wallet = 0.6
threshold_metamask_select = 0.6
threshold_unlock_img = 0.8
threshold_sign_img = 0.8
threshold_error = 0.5
threshold_back = 0.7
threshold_hero_icon = 0.3
threshold_work = 0.7
threshold_treasure = 0.5

general_check_time = 60
hero_work_interval = 20
hero_refresh_interval = 5
refresh_every_mins = 120

hero_sent_count = 0
login_attempts = 0
pyautogui.FAILSAFE = False

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

def click_btn(coordinates, insist="no"):
    click_tries = 0
    while click_tries < 3:
        if coordinates is not False:
            x,y,w,h = coordinates[0]
            pyautogui.moveTo(x+w/2,y+h/2,1)
            pyautogui.click()
            click_tries = 0
            return True
        elif insist == "yes":
            click_tries += 1
            time.sleep(5)
        else:
            return False

def login():
    global login_attempts

    if click_btn(get_coord(connect_wallet_img, threshold_connect_wallet)):
        sys.stdout.write("\nFound login button.")
        sys.stdout.flush()
        time.sleep(3)

    if click_btn(get_coord(metamask_select_img, threshold_metamask_select)):
        sys.stdout.write("\nFound metamask button.")
        sys.stdout.flush()
        time.sleep(8)
    

    metamask_unlock_coord = get_coord(metamask_unlock_img, threshold_unlock_img)
    if metamask_unlock_coord is not False:
        sys.stdout.write("\nFound unlock button. Waiting 30 seconds for password")
        sys.stdout.flush()
        time.sleep(30)
        click_btn(metamask_unlock_coord)
        time.sleep(5)

    time.sleep(3)

    if click_btn(get_coord(metamask_sign_img, threshold_sign_img)):
        sys.stdout.write("\nFound sign button. Waiting 30s to check if logged in.")
        sys.stdout.flush()
        time.sleep(30)

    if current_screen() == "main":
        sys.stdout.write("\nLogged in.")
        sys.stdout.flush()
        return True
    else:
        sys.stdout.write("\nLogin failed. Trying again.")
        sys.stdout.flush()
        login_attempts += 1

        if (login_attempts > 3):
            sys.stdout.write("\n>3 login attemps. Retrying.")
            sys.stdout.flush()
            pyautogui.hotkey('ctrl', 'f5')
            login_attempts = 0

            if click_btn(get_coord(metamask_cancel_button, threshold_unlock_img)):
                sys.stdout.write("\nMetamask is glitched. Fixing.")
                sys.stdout.flush()
            
            time.sleep(8)

        login()

    handle_error()

def handle_error():
    if get_coord(error_img, threshold_error) is not False:
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        sys.stdout.write("\nError detected. Trying to resolve. ")
        sys.stdout.write(current_time)
        sys.stdout.flush()
    else:
        return False

    if click_btn(get_coord(error_ok_img, threshold_connect_wallet)):
        sys.stdout.write("\nRefreshing page. ")
        sys.stdout.write(current_time)
        sys.stdout.flush()
        pyautogui.hotkey('ctrl', 'f5')
        time.sleep(15)
        login()

def current_screen():
    if get_coord(back_button_img, threshold_back) is not False:
        return "thunt"
    elif get_coord(treasure_hunt_img, threshold_error) is not False:
        return "main"
    elif get_coord(connect_wallet_img, threshold_connect_wallet) is not False:
        return "login"
    elif get_coord(character_indicator, threshold_error) is not False:
        return "character"
    else:
        return "unknown"
    
def heroes_work(): 
    global hero_sent_count

    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)

    sys.stdout.write("\nSending heroes to work! ")
    sys.stdout.write(current_time)
    sys.stdout.flush()

    if current_screen() == "thunt":
        if click_btn(get_coord(back_button_img, threshold_back)):
            time.sleep(6)

    if current_screen() == "main":
        if click_btn(get_coord(hero_icon, threshold_hero_icon)):
            time.sleep(10)

    if current_screen() == "character":
        width, height = pyautogui.size()
        pyautogui.moveTo(width/2, height/2)
        pyautogui.scroll(-150)

        work_button_list = get_coord(work_rest, threshold_work)
        while work_button_list is not False:
            x,y,w,h = work_button_list[-1]
            
            pyautogui.moveTo(x-10+w/2,y+h/2,1)
            pyautogui.click()
            hero_sent_count += 1
            sys.stdout.write("\nHeroes sent to work: ")
            sys.stdout.write(str(hero_sent_count))
            sys.stdout.flush()
            time.sleep(4)

            handle_error()
            
            work_button_list = get_coord(work_rest, threshold_work)
            time.sleep(4)
        
        time.sleep(5)

        if click_btn(get_coord(character_close_button, threshold_back)):
            sys.stdout.write("\nFinished putting to work.")
            sys.stdout.flush()
            return True
        else:
            sys.stdout.write("\nCouldn't send characters to work, trying again later.")
            sys.stdout.flush()
            return False
        
    time.sleep(5)

    if current_screen() == "unknown":
        check_for_logout()

def refresh_heroes():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)

    sys.stdout.write("\nRefreshing heroes. ")
    sys.stdout.write(current_time)
    sys.stdout.flush()
    if current_screen() == "thunt":
        if click_btn(get_coord(back_button_img, threshold_back)):
            time.sleep(5)
    if current_screen() == "main":
        if click_btn(get_coord(treasure_hunt_img, threshold_treasure)):
            return True
        else:
            return False
    else:
        return False

def check_for_logout():
    if current_screen() == "unknown":
        if get_coord(connect_wallet_img, threshold_connect_wallet) or get_coord(metamask_select_img, threshold_metamask_select) or get_coord(metamask_sign_img, threshold_sign_img) is not False:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            sys.stdout.write("\nLogout detected. Login in. ")
            sys.stdout.write("\nRefreshing page. ")
            sys.stdout.write(current_time)
            sys.stdout.flush()
            pyautogui.hotkey('ctrl', 'f5')
            time.sleep(15)
            login()
        else:
            return False
            
    else:
        return False

def main():
    last = {
    "heroes_work" : 0,
    "new_map" : 0,
    "refresh_heroes" : 0,
    "refresh_page" : 0
    }

    while True:
        if current_screen() == "login":
            login()
            time.sleep(5)
        
        handle_error()

        now = time.time()
        if now - last["heroes_work"] > hero_work_interval * 60: ## Check to see if heroes have been sent to work in the last n minutes
            if heroes_work():
                last["heroes_work"] = now ## Update latest time            
                time.sleep(3)
        
        if current_screen() == "main":
            if click_btn(get_coord(treasure_hunt_img, threshold_treasure)):
                sys.stdout.write("\nEntering treasure hunt")
                sys.stdout.flush()
            
        if current_screen() == "thunt":
            if click_btn(get_coord(new_map, threshold_connect_wallet)):
                sys.stdout.write("\nNew map!")
                sys.stdout.flush()
                last["new_map"] = now
        
        now = time.time()
        if now - last["refresh_heroes"] > hero_refresh_interval * 60:
            if refresh_heroes():
                last["refresh_heroes"] = now
                time.sleep(3)
        
        if current_screen() == "character":
            click_btn(get_coord(character_close_button, threshold_back))
            time.sleep(3)

        check_for_logout()
        sys.stdout.flush()
        time.sleep(general_check_time)

main()
