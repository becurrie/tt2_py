"""
imagesearch.py

External wrapping library taken from https://github.com/drov0/python-imagesearch/blob/master/imagesearch.py
Provides some helpful functions used by the Bot Grabber instance to search for images on screen.
"""
import cv2
import numpy as np
import pyautogui
import random
import time


def region_grabber(region):
    """
    grabs a region (topx, topy, bottomx, bottomy)
    to the tuple (topx, topy, width, height)

    input : a tuple containing the 4 coordinates of the region to capture
    output : a PIL image of the area selected.
    """
    x1 = region[0]
    y1 = region[1]
    width = region[2] - x1
    height = region[3] - y1

    return pyautogui.screenshot(region=(x1, y1, width, height))


def imagesearcharea(image, x1, y1, x2, y2, precision=0.8, im=None):
    """
    Searches for an image within an area

    input :
    image : path to the image file (see opencv imread for supported types)
    x1 : top left x value
    y1 : top left y value
    x2 : bottom right x value
    y2 : bottom right y value
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
    im : a PIL image, useful if you intend to search the same unchanging region for several elements

    returns :
    the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not
    """
    if im is None:
        im = region_grabber(region=(x1, y1, x2, y2))

    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc


def click_image(image, pos, action, timestamp, offset=5, pause=0):
    """
    Click on the center of an image with a bit of random.
    eg, if an image is 100*100 with an offset of 5 it may click at 52,50 the first time and then 55,53 etc
    Useful to avoid anti-bot monitoring while staying precise.

    this function doesn't search for the image, it's only meant for easy clicking on the images.

    input :
    image : path to the image file (see opencv imread for supported types)
    pos : array containing the position of the top left corner of the image [x,y]
    action : button of the mouse to activate : "left" "right" "middle", see pyautogui.click documentation for more info
    time : time taken for the mouse to move from where it was to the new position
    """
    img = cv2.imread(image)
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + r(width / 2, offset), pos[1] + r(height / 2, offset), timestamp)
    pyautogui.click(button=action, pause=pause)


def imagesearch(image, precision=0.8):
    """
    Searches for an image on the screen

    input :
    image : path to the image file (see opencv imread for supported types)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
    im : a PIL image, useful if you intend to search the same unchanging region for several elements

    returns :
    the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not
    """
    im = pyautogui.screenshot()
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc


def imagesearch_loop(image, timesample, precision=0.8):
    """
    Searches for an image on screen continuously until it's found.

    input :
    image : path to the image file (see opencv imread for supported types)
    time : Waiting time after failing to find the image
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

    returns :
    the top left corner coordinates of the element if found as an array [x,y]
    """
    pos = imagesearch(image, precision)
    while pos[0] == -1:
        print(image+" not found, waiting")
        time.sleep(timesample)
        pos = imagesearch(image, precision)
    return pos


def imagesearch_num_loop(image, timesample, max_samples, precision=0.8):
    """
    Searches for an image on screen continuously until it's found or max number of samples reached.

    input :
    image : path to the image file (see opencv imread for supported types)
    time : Waiting time after failing to find the image
    maxSamples: maximum number of samples before function times out.
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

    returns :
    the top left corner coordinates of the element if found as an array [x,y]
    """
    pos = imagesearch(image, precision)
    count = 0
    while pos[0] == -1:
        print(image+" not found, waiting")
        time.sleep(timesample)
        pos = imagesearch(image, precision)
        count = count + 1
        if count > max_samples:
            break
    return pos


def imagesearch_region_loop(image, timesample, x1, y1, x2, y2, precision=0.8):
    """
    Searches for an image on a region of the screen continuously until it's found.

    input :
    image : path to the image file (see opencv imread for supported types)
    time : Waiting time after failing to find the image
    x1 : top left x value
    y1 : top left y value
    x2 : bottom right x value
    y2 : bottom right y value
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

    returns :
    the top left corner coordinates of the element as an array [x,y]
    """
    pos = imagesearcharea(image, x1, y1, x2, y2, precision)

    while pos[0] == -1:
        time.sleep(timesample)
        pos = imagesearcharea(image, x1, y1, x2, y2, precision)
    return pos


def imagesearch_count(image, precision=0.9):
    """
    Searches for an image on the screen and counts the number of occurrences.

    input :
    image : path to the target image file (see opencv imread for supported types)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.9

    returns :
    the number of times a given image appears on the screen.
    optionally an output image with all the occurrences boxed with a red outline.
    """
    img_rgb = pyautogui.screenshot()
    img_rgb = np.array(img_rgb)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= precision)
    count = 0
    for pt in zip(*loc[::-1]):  # Swap columns and rows
        count = count + 1

    return count


def r(num, rand):
    return num + rand*random.random()
