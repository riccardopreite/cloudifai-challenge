import os, json, sys
from sre_parse import CATEGORIES
import numpy as np
# import pandas as pd
import xml.etree.ElementTree as ET
import cv2

MAX_WIDTH = 800
MAX_HEIGHT = 450

COCO_DATA = json.load(open('coco_input/instances_val2017.json'))
COCO_ANNOTATIONS = COCO_DATA["annotations"]
COCO_CATEGORIES = COCO_DATA["categories"]


COCO_JSON =  {
        "categories": [],
        "images": [],
        "annotations": []
}
CATEGORIES = []
CATEGORIES_FORMAT = {
    "category": {
        "id": int,
        "name": str,
        "supercategory": str
    }
}

IMAGE = []
IMAGE_FORMAT = {
 "id": int,
 "width": int,
 "height": int,
 "file_name": str
}
ANNOTATION=[]
ANNOTATION_FORMAT = {
 "id": id,
 "image_id": int,
 "category_id": int,
 "bbox": [] #x, y, width, height
}

def check_exist(path):
    return os.path.exists(path)

def init_check(imagedir, xmldir, outputdir):
    if not check_exist(imagedir):
        print("Cartella immagini non trovata")
        sys.exit(1)
    if not check_exist(xmldir):
        print("Cartella xml non trovata")
        sys.exit(1)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

def check_file(image, xml):
    check = True
    if image[-3::] != "jpg":
        print(image, "is not jpg format")
        check = False
    if xml[-3::] != "xml":
        print(xml, "is not xml format")
        check = False
    return check
    
def resize_image(img, image_path, imagedir, outputdir):
    new_image = cv2.resize(img, (MAX_WIDTH, MAX_HEIGHT))
    new_img_path = image_path.replace(imagedir, outputdir)
    cv2.imwrite(new_img_path, new_image)
    
def resize_bndbox(bounded, scalex, scaley):
    old_xmin = int(bounded.find("xmin").text)
    old_xmax = int(bounded.find("xmax").text)
    old_ymin = int(bounded.find("ymin").text)
    old_ymax = int(bounded.find("ymax").text)
    
    bounded.find("xmin").text = str(old_xmin/scalex)
    bounded.find("xmax").text = str(old_xmax/scalex)

    bounded.find("ymin").text = str(old_ymin/scaley)
    bounded.find("ymax").text = str(old_ymax/scaley)


def get_coco_data(xml_tree):
    tmp_categories = []
    tmp_img = IMAGE_FORMAT
    tmp_cat = CATEGORIES_FORMAT
    tmp_ann = ANNOTATION_FORMAT
    
    file_name = xml_tree.find("filename").text
    width = int(xml_tree.find("size").find("width").text)
    height = int(xml_tree.find("size").find("height").text)
    tmp_img["width"] = width
    tmp_img["height"] = height
    tmp_img["file_name"] = file_name
    tmp_img["id"] = int(file_name.split(".")[0])

    objects = xml_tree.find("object")
    for obj in objects:
        tmp_cat = CATEGORIES_FORMAT 
        category_name = obj.find("name").text
        for category in COCO_CATEGORIES:
            if category['name'] == category_name:
                tmp_cat["id"] = category["id"]
                tmp_cat["name"] = category_name
                tmp_cat["supercategory"] = category["supercategory"]
                tmp_categories.append(tmp_cat)
    
    
    return tmp_categories, tmp_img, []
def iterate_file(image_files, xml_files, imagedir, xmldir, outputdir):
    for image_path, xml_path in zip(image_files,xml_files):
        if check_file(image_path, xml_path):
            xml_tree = ET.parse(xml_path)
            
            width_tag = xml_tree.find('size').find('width')
            height_tag = xml_tree.find('size').find('height')
            width_text = int(width_tag.text)
            height_text = int(height_tag.text)
            img = cv2.imread(image_path)

            if width_text > MAX_WIDTH or height_text > MAX_HEIGHT:
                width_tag.text = str(MAX_WIDTH)
                height_tag.text = str(MAX_HEIGHT)
                resize_image(img, image_path,  imagedir, outputdir)

                bounding_boxes = xml_tree.findall('object')
                scalex = width_text/MAX_WIDTH
                scaley = height_text/MAX_HEIGHT
                
                for box in bounding_boxes:
                    bndbox = box.findall('bndbox')
                    for bounded in bndbox:
                        resize_bndbox(bounded, scalex, scaley)
            else:
                new_img_path = image_path.replace(imagedir, outputdir)
                cv2.imwrite(new_img_path, img)

        new_xml_path = xml_path.replace(xmldir, outputdir)
        out_file = open(new_xml_path,"wb")
        xml_tree.write(out_file,encoding='utf-8')
        out_file.close()

        # category, image, annotation = get_coco_data(xml_tree)

        
        
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Errato numero di parametri in input")
        sys.exit(1)

    imagedir = sys.argv[1]
    xmldir = sys.argv[2]
    outputdir = sys.argv[3]
    if outputdir[-1] != '\\':
        outputdir += '\\'
    init_check(imagedir, xmldir, outputdir)

    image_files = [os.path.join(imagedir,img) for img in os.listdir(imagedir)]
    xml_files = [os.path.join(xmldir,xml) for xml in os.listdir(xmldir)]

    iterate_file(image_files, xml_files, imagedir, xmldir, outputdir)

    

    


