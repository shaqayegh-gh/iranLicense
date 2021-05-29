import os
import sys
import glob
from math import ceil

import cv2
from PIL import Image, ImageFilter, ImageDraw
import dlib
import time
import numpy as np
from pandas import DataFrame
from sklearn.cluster import KMeans
from findplate import findplate
from skimage.filters import sobel


# In this example we are going to train a plate  detector based on the small
# plate dataset in the car_plates/ directory.  This means you need to supply
# the path to this plates folder as a command line argument so we will know
# where it is.
def splitcharacter(imagein, find_plate):
    img_arr2 = dlib.as_grayscale(imagein)
    img_arr2 = dlib.threshold_image(img_arr2)


    # --------------------------------------------
    xmargin = ceil(float(lendiff) / 8)
    ymargin = ceil(float(hdiff * 9) / 2)
    img = 255 - img_arr2
    h = img.shape[0]
    w = img.shape[1]

    # print(h, w, "<==")
    # find blank columns:
    white_num = []
    white_max = 0
    for i in range(w):
        white = 0
        for j in range(h):
            # print(img[j,i])
            if img[j, i] < 127:
                white += 1
        white_num.append(white)
        white_max = max(white_max, white)
    blank = []
    # print("whitre_max=%d,%f" % (white_max, 0.895 * white_max))
    for i in range(w):

        if (white_num[i] > 0.895 * white_max):
            blank.append(True)

        else:
            blank.append(False)

    # split index:
    i = 0
    num = 0
    l = 0
    x, y, d = [], [], []
    while (i < w):
        if blank[i]:
            i += 1
        else:
            j = i
            while (j < w) and ((not blank[j]) or (j - i < 10)):
                j += 1
            x.append(i)
            y.append(j)
            d.append(j - i)
            l += 1
            i = j
    # print("len=%d" % l)
    failbox = []
    whitesum = 0

    avgdiff2 = round(w / 8)
    avgdiff = 0  # avgdiff2
    sumavg = 1

    for k in range(l):
        # print(x[k], y[k], d[k], avgdiff, d[k] / avgdiff2)
        if d[k] / avgdiff2 < 1:
            avgdiff = (avgdiff + d[k] * 1.0) / 2

    avgdiff = avgdiff + xmargin
    if l <= 4:
        avgdiff = round((w - 10 * xmargin) / 8)

    # print("*(%d)*" % avgdiff)
    if l < 8:
        k = 0
        while k < l:
            # print(k, d[k] / avgdiff, x[k], y[k], d[k])
            if (d[k] * 1.0) / avgdiff > 1.80:
                dn = d[k] - avgdiff
                d[k] = avgdiff
                yn = y[k]
                if k == 6:
                    x[k] = x[k] + xmargin
                    xn = x[k] + avgdiff + xmargin * 1
                    y[k] = x[k] + avgdiff
                elif k == 2:
                    d[k] = avgdiff * 2;
                    y[k] = x[k] + 2 * avgdiff + xmargin
                    xn = x[k] + avgdiff * 2 + xmargin * 2
                else:
                    xn = x[k] + avgdiff + xmargin
                    y[k] = x[k] + avgdiff
                # k=k+1
                if yn <= xn:
                    k = k + 1
                    continue
                x.insert(k + 1, xn)
                y.insert(k + 1, yn)
                d.insert(k + 1, dn)
                # print(k, x[k], y[k], d[k])
                # print(xn, yn, dn)
                l = l + 1
                if l == 8:
                    break
            k = k + 1

    for k in range(l):
        for i in range(int(x[k]), int(y[k])):
            whitesum += white_num[i]
        failbox.append((100 * whitesum) / (h * (int(y[k]) - int(x[k]))))
        whitesum = 0

    for k in range(l):
        if round((d[k] * 1.0) / avgdiff) > 1 and l >= 8:
            if k == 0:
                x[k] = x[k] + avgdiff
            elif k == l - 1:
                y[k] = y[k] - avgdiff
                if y[k] - x[k] < avgdiff:
                    y[k] = x[k] + avgdiff + xmargin
        if round((d[k] * 1.0) / avgdiff) < 1:
            failbox[k] = 2
        # print(x[k], y[k], round((d[k] * 1.0) / avgdiff))

    # print(failbox)
    # print("<===============>")
    realidx = 0
    while l > 8:
        for k in range(len(failbox)):
            if failbox[k] < 33:
                del x[realidx]
                del y[realidx]
                del d[realidx]
                failbox[k] = -1
                l = l - 1
            else:
                realidx += 1
        k = 0
        lk = len(failbox)
        while k < lk:
            if failbox[k] == -1:
                del failbox[k]
                lk = lk - 1
            else:
                k = k + 1
        # print(failbox)
        for ifl in range(8, l):
            doval = min(failbox)
            doval_idx = failbox.index(doval)
            del x[doval_idx], y[doval_idx], d[doval_idx], failbox[doval_idx]
            l = l - 1

    realidx = 0
    for k in range(len(failbox)):
        if k >= len(failbox):
            break

        if failbox[k] < 20:
            del x[realidx]
            del y[realidx]
            del d[realidx]
            del failbox[k]
            l = l - 1
        else:
            realidx += 1

    if l < 8:
        k = 0
        while k < l:
            # print(k, d[k] / avgdiff, x[k], y[k], d[k])
            if (d[k] * 1.0) / avgdiff > 1.80:
                dn = d[k] - avgdiff
                d[k] = avgdiff
                yn = y[k]
                if k == 6:
                    x[k] = x[k] + xmargin
                    xn = x[k] + avgdiff + xmargin * 1
                    y[k] = x[k] + avgdiff
                elif k == 2:
                    d[k] = avgdiff * 2;
                    y[k] = x[k] + 2 * avgdiff + xmargin
                    xn = x[k] + avgdiff * 2 + xmargin * 2
                else:
                    xn = x[k] + avgdiff + xmargin
                    y[k] = x[k] + avgdiff
                # k=k+1
                if yn <= xn:
                    k = k + 1
                    continue
                x.insert(k + 1, xn)
                y.insert(k + 1, yn)
                d.insert(k + 1, dn)
                # print(k, x[k], y[k], d[k])
                # print(xn, yn, dn)
                l = l + 1
                if l == 8:
                    break
            k = k + 1
    # print("--------%d---------------------------------" % l)
    # --------------------------------------------
    # print (type(img_arr2))
    # print(" ")
    # print(img_arr2)
    # img_arr2=sobel(img_arr2)
    img1 = Image.fromarray(img_arr2)

    img1.save(f'out/final.jpg')
    img2 = dlib.load_rgb_image('out/final.jpg')
    ximg, yimg = img1.size
    # print(img1.size, img2.shape)
    img2 = img2[2 * int(yimg / 4):3 * int(yimg / 4), 0:ximg]

    img_arr = dlib.as_grayscale(img2)
    img_arr = dlib.threshold_image(img_arr)

    Data = {'x': [], 'y': []}
    for y2 in range(len(img_arr)):
        for x2 in range(len(img_arr[0])):
            if img_arr[y2][x2] < 128:
                Data['x'].append(x2)
                Data['y'].append(y2)

    df = DataFrame(Data, columns=['x', 'y'])
    cluster = 10
    try:
        kmeans = KMeans(n_clusters=cluster).fit(df)
    except Exception as e:
        return None
    centroids = kmeans.cluster_centers_

    # print(len(centroids),centroids)
    centroids = sorted(centroids, key=lambda x2: x2[0])
    # centroids.reverse();
    # print(centroids)
    imageofnumber = []
    # print("==>", xmargin, ymargin)
    imagefinal = ImageDraw.Draw(img1)

    for k in range(l):
        imagefinal.rectangle(((x[k], 1), (y[k], yimg - 1)), outline="green")

    img1.show()
    firstx = 0
    xstep = 0

    for i in range(l):
        # print(x[i], y[i])
        if x[i] < 3:
            x[i] = 3
        if y[i] > w - 2:
            y[i] = w - 2

        imageofnumber.append(imagein[0:int(yimg), int(x[i] - 2):int(y[i]) + 2])
    return imageofnumber


if __name__ == "__main__":
    if len(sys.argv) != 2:
        # print(
        #     "Give the path to the car plates directory as the argument to this "
        #     "program."
        #     "execute this program by running:\n"
        #     "    ./read_car_plates_dlib.py car_plates/")
        plate_folder = "car_plates/"
        # exit()
    else:
        plate_folder = sys.argv[1]

    find_plate = findplate()
    options = dlib.simple_object_detector_training_options()

    options.add_left_right_image_flips = True

    options.C = 50
    options.epsilon = 0.00001
    options.num_threads = 4
    options.be_verbose = True

    training_xml_path = os.path.join(plate_folder, "training.xml")
    testing_xml_path = os.path.join(plate_folder, "testing.xml")

    # print(options)


    # print("")  # Print blank line to create gap from previous output

    detector = dlib.simple_object_detector("detector.svm")

    # We can look at the HOG filter we learned.  It should look like a plate.  Neat!
    # win_det = dlib.image_window()
    # win_det.set_image(detector)

    # print("Showing detections on the images in the plates folder...")
    win = dlib.image_window()
    global lendiff, hdiff

    file_list = []
    if plate_folder.find(".jpg", -4) > -1:
        file_list.append(plate_folder)
    else:
        file_list = glob.glob(os.path.join(plate_folder, "*.jpg"))

    for f in file_list:  # glob.glob(os.path.join(plate_folder, "*.jpg")):
        # print("Processing file: {}".format(f))
        img = dlib.load_rgb_image(f)

        dets = detector(img)
        # print("Number of plate detected: {}".format(len(dets)))
        for k, d in enumerate(dets):
            # print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(),
            #                                                                    d.bottom()))
            lendiff = (d.right() - d.left()) / 11
            hdiff = (d.bottom() - d.top()) / 9
            top = int(d.top() - hdiff)
            bottom = int(d.bottom() + hdiff)
            left = int(d.left() + lendiff / 2)
            right = int(d.right() + lendiff)
            if top < 0:
                top = 0
            if left < 0:
                left = 0
            imgnew = img[top:bottom, left:right]
            ####---------------Find Character---------------
            charsplited = splitcharacter(imgnew, find_plate)
            cnt = 0
            for isp in charsplited:
                win.set_image(isp)
                # print(isp)
                imgs = Image.fromarray(isp)
                imgs.save(str(cnt) + ".jpg")
                cnt += 1

            imagess = []
            for i in range(cnt):
                imgss = dlib.load_rgb_image(str(i) + ".jpg")
                imagess.append(imgss)
                # cv2.imshow('chhar',imgss)
                # cv2.waitKey(0)
            # print(find_plate.get_platestr_from_image(imagess))  # charsplited))

            dlib.hit_enter_to_continue()

        if len(dets) == 0:
            dlib.hit_enter_to_continue()

    print("finished.....")
    dlib.hit_enter_to_continue()
