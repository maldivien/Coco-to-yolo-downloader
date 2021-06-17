import sys, getopt
import argparse
from pycocotools.coco import COCO
import requests
import os
import json
from os import listdir, getcwd
from os.path import join
from functools import reduce
from random import shuffle
import threading
    
def convert(size,box):
    dw = 1./size[0]
    dh = 1./size[1]
    xmin = box[0]
    ymin = box[1]
    xmax = box[2] + box[0]
    ymax = box[3] + box[1]
            
    x = (xmin + xmax)/2
    y = (ymin + ymax)/2     
    w = xmax - xmin
    h = ymax-ymin
            
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h,)

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def filter_coco(T):
    return (coco_names.index(T[0]) + 1)

def download_coco(catid, catname, classid, download_limit):
    print("Starting Thread for " + catname)
    imgIds = coco.getImgIds(catIds=[catid])
    images = coco.loadImgs(imgIds)
    print(str(len(images)) + " Images found for " + catname)
    ann_ids = coco.getAnnIds(catIds=[catid], iscrowd=None)
    all_ann = coco.loadAnns(ann_ids)
    print(str(len(all_ann)) + " Annotations found for "+ catname)
    print("Download Started...! Category: "+ catname)
    counter = 0
    for im in images:
        if counter == limit:
            print("Limit of " + str(counter) + " Images download for class " + cateogry +".")
            break
        image_id = im['id']
        width = im['width']
        height = im['height']
        filename = im["file_name"]
        if os.path.isfile(str(output_folder + filename)):
            print("Skipping... "+str(output_folder + filename))
            continue
        all_annotations = list(filter(lambda item1: item1['image_id'] == image_id,all_ann))
        annotations = list(filter(lambda item3: item3['category_id'] == catid, all_annotations))
        if annotations:
            counter += 1
            with open(output_folder +'%s.txt'%(filename[:-4]), 'a+') as outfile:
                for annotation in annotations:
                    box = annotation['bbox']
                    bb = convert((width,height),box)
                    outfile.write(str(classid)+" "+" ".join([str(b) for b in bb]) + '\n')
                    
            outfile.close()
            img_data = requests.get(im['coco_url']).content
            with open(output_folder + filename, 'wb') as handler:
                handler.write(img_data)
    print("Download Completed! Category: "+ catname)            

def download_negatives(output_path, limit):
    print("[Negatives] Starting Thread")
    filtered_coco = [i for i in coco_names if i not in category_names] 
    imgIds = coco.getImgIds()
    images = coco.loadImgs(imgIds)
    print(str(len(images)) + " Images found." )
    ann_ids = coco.getAnnIds(iscrowd=None)
    all_ann = coco.loadAnns(ann_ids)
    print(str(len(all_ann)) + " Annotations found.")
    counter = 0
    print("Shuffling Dataset...")
    shuffle(images)
    print("Download Started...")
    for im in images:
        
        if counter == limit:
            print("Limit of " + str(counter) + " Images download for class " + cateogry +".")
            break
        image_id = im['id']
        width = im['width']
        height = im['height']
        filename = im["file_name"]
        if os.path.isfile(str(output_path + filename)):
            print("Skipping... "+str(output_path + filename))
            continue
        annotations = list(filter(lambda item1: item1['image_id'] == image_id,all_ann))
        found_annotations = False
        annotations_filter = []
        for catstoremove in category_ids:
            annotations_filter = list(filter(lambda item3: item3['category_id'] == catstoremove, annotations))
            if annotations_filter:
                found_annotations = True
                break


        if not found_annotations:
            counter += 1
            with open(output_path +'%s.txt'%(filename[:-4]), 'a+') as outfile:
                outfile.close()
            
            img_data = requests.get(im['coco_url']).content
            with open(output_path + filename, 'wb') as handler:
                handler.write(img_data)
     


def main():
    global coco_names
    global output_folder  
    global coco
    global category_ids
    global category_names

    negative = False
    download_limit = 500
    output_folder = "annotations/obj/"
    negatives_folder = "annotations/negatives/"
    os.makedirs(output_folder, exist_ok=True) 
    os.makedirs(negatives_folder, exist_ok=True) 

    parser = argparse.ArgumentParser(description='COCO Dataset to Yolo downloader')
    parser.add_argument('-o','--opt', help='use Negatives to download negatives', required=False)
    parser.add_argument('-l','--limit', help='Image download limit per class or total for negatives', required=False)
    args = vars(parser.parse_args())

    if args['opt'] == 'negatives':
        negative = True
    if args['limit']:
        download_limit = args['limit']

    print("Download Limit: " + str(download_limit))


    with open("categories_to_download.txt") as file:
        categories_intrest = [line.rstrip('\n').split(', ') for line in file]
        
    with open("coco-names.txt") as file:
       
        coco_names = [line.rstrip('\n') for line in file]
         
    coco = COCO('instances_train2017.json')
    coco.info()
    category_ids = list(map(filter_coco, categories_intrest))  
    category_names = [row[0] for row in categories_intrest]

    
    
    if negative:
        print(category_ids)
        download_negatives(negatives_folder, download_limit)
    else:
        catIds = coco.getCatIds(catNms=category_names)
        threads = [category_ids]
        try:
            for catid in catIds:
                catname = coco_names[catid - 1]
                #custom classId to be added to annotation file
                classid = [x for x in categories_intrest if str(catname) in x][0][1]

                thread = threading.Thread(target=download_coco, args=(catid,catname, classid, download_limit)) 
                thread.daemon = True
                threads.append(thread)
                
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            while len(threads) > 0:
                threads = [t.join(1000) for t in threads if t is not None and t.isAlive()]
        except KeyboardInterrupt:
            print("Ctrl-c received! Sending kill to threads...")
            for t in threads:
                t.kill_received = True

        print("COCO dataset download completed.")    
    
if __name__ == "__main__": main() 

      



