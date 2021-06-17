# Coco to Yolo Downloader (Images, Annoatations, Negatives)

- Downloads COCO dataset images by multiple categories in parallel threads, converts COCO annotations to YOLO format and stored in respective .txt files
- Download Negative images which excludes the categories in categories_to_download.txt
- Can include custom class numbers to be added to annoation, just add desired numbers to categories_to_download.txt

Requirements:
-pip3 install pycococtools
-coco Dataset "instances_train2017.json" file

Run:
-To download coco dataset: python3 main.py -o download -l 5000 
-To download negatives from coco dataset: python3 main.py -o negatives -l 1000 

