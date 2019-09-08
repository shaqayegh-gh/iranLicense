from pandas import DataFrame
from sklearn.cluster import KMeans
from sklearn import datasets , svm , metrics
from PIL import Image , ImageDraw
import numpy as np
import os
from skimage import io
from skimage.color import rgb2gray
from skimage.filters import sobel

class findplate:
    def __init__(self):
        ################custom train
        dataimage=[]
        target=[]
        train_imgs=os.listdir('train/')
        cnt=0
        dict_label={}
        size=28,42
        for train_img in train_imgs:
            #print(train_img)
            img_label=train_img.split('.')[0]
            img_label=img_label[:-1]
            img_label=img_label.rjust(3,' ')
            try:
                img=Image.open("train/"+train_img)
                img=img.resize((28,42), Image.ANTIALIAS)
                #data_img=rgb2gray(io.imread("train/"+train_img,as_gray=True))
                #data_img=sobel(data_img)
                img=img.convert('L')
                data_img=np.asarray(img,dtype="int32")
                data_img=np.concatenate(data_img,axis=0)
                print(data_img)
                print("-------------------"+train_img)
                print(img_label)
                cnt +=1
                if not dict_label.has_key(img_label):
                    dict_label[img_label]=cnt
                dataimage.append(data_img)
                target.append(img_label)
            except IOError:
                pass
        
        print("-------------------",len(dataimage))
        self.classifier = svm.SVC(gamma=0.000001 , C=100.)
        self.classifier.fit(dataimage, target)

       
    def __read_image(self,image):

        #mage=Image.open('test.jpg')
        #image=image.rotate(180)
        #crope=(30,10,155,80)
        #image=image.crop(crope)
    
        #img_arr=np.asarray(image,dtype='int32')
        img_arr=image
        #imagefinal=ImageDraw.Draw(image)
        #for point in centroids:
            #imagefinal.rectangle(((point[0]-15,point[1]-20),(point[0]+15,point[1]+23)),outline="black")
        #image.show()
        dataimage=[]
        predicted = self.classifier.predict(img_arr)
        self.number_string=''
        for i in predicted:
            self.number_string+=str(i)
        ############################

    def get_platestr_from_image(self,src_img):
        self.__read_image(src_img)
        return self.number_string