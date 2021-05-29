import cv2
import easyocr
import imutils
from skimage.filters import threshold_local
import pytesseract

for i in range(8):
    chars = cv2.imread(f'{i}.jpg')

    V = cv2.split(cv2.cvtColor(chars, cv2.COLOR_BGR2HSV))[2]
    T = threshold_local(V, 29, offset=15, method='gaussian')
    thresh = (V > T).astype("uint8") * 255
    thresh = cv2.bitwise_not(thresh)

    plate = imutils.resize(chars, width=32)
    thresh = imutils.resize(thresh, width=32)
    cv2.imshow("thresh", thresh)
    cv2.waitKey(0)

    # pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    # # img = cv2.imread(thresh)
    # text = pytesseract.image_to_string(thresh,lang="fas")
    # read = text.encode('utf-8')

    reader = easyocr.Reader(lang_list=['fa'])
    text = reader.readtext(chars)
    print(text)
    # with open('out.txt','a') as outfile:
    #     outfile.write(text)


    # print(text)