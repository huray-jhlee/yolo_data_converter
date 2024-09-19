import os
import cv2
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
from sqlalchemy import create_engine
from config import DevServer, MainServer

# visualization yolo label
def draw_bbox(image, bbox, color=(0, 255, 0), thickness=2):
    bbox = [int(x) for x in bbox]
    cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, thickness)
    return image

def draw_with_label(image_path, bbox_info):
    img_obj = cv2.imread(image_path)
    img_obj = cv2.cvtColor(img_obj, cv2.COLOR_BGR2RGB)
    img_width, img_height, _ = img_obj.shape
    
    if isinstance(bbox_info, list):
        bbox_info_list = bbox_info
    
    elif isinstance(bbox_info, str) and os.path.isfile(bbox_info):
        with open(bbox_info, 'r') as f:
            label_datas = f.readlines()
        bbox_info_list = [list(map(float, x.strip().split(" ")))[1:] for x in label_datas]
    else :
        raise Exception("invalid bbox_info")
    
    for x_center, y_center, bbox_width, bbox_height in bbox_info_list:
        x_center *= img_width
        y_center *= img_height
        bbox_width *= img_width
        bbox_height *= img_height
        
        x_min = x_center - (bbox_width / 2)
        x_max = x_center + (bbox_width / 2)
        y_min = y_center - (bbox_height / 2)
        y_max = y_center + (bbox_height / 2)
        
        draw_obj = draw_bbox(img_obj, [x_min, y_min, x_max, y_max])
    
    return draw_obj

def convert_to_yolo_format(bbox, width, height):
    bbox = list(map(int, bbox))
    
    x_min, y_min, x_max, y_max = bbox
    x_center = (x_min + x_max) / 2.0
    y_center = (y_min + y_max) / 2.0
    
    box_width = x_max - x_min
    box_height = y_max - y_min
    
    norm_x_center = x_center / width
    norm_y_center = y_center / height
    norm_box_width = box_width / width
    norm_box_height = box_height / height
    
    return [norm_x_center, norm_y_center, norm_box_width, norm_box_height]

def main(args):
    
    # make name_to_id
    query = f"""
    SELECT change_class_name AS class_name, merge_class_id AS class_id
    FROM food_id_name_table
    WHERE check_use = 'Y'
    """
    df = pd.read_sql(query, ENGINE)
    name_to_id = {}
    for _, row in df.iterrows():
        class_name, class_id = row['class_name'], row['class_id']
        name_to_id[class_name] = class_id
    
    print("make name_to_id dict, Done")
    
    # get df with target class_id
    if args.class_name in name_to_id:
        class_id = name_to_id[args.class_name]
    else :
        raise Exception("Invalid class name")
    
    query = f"""
    SELECT h.idx AS image_id, c.org_path AS original_path, c.crop_info, h.class_id, h.check_class_id
    FROM huray_image_data AS h
    JOIN crop_table AS c
    ON h.idx = c.idx
    WHERE h.check_class_id = {class_id}
    """
    df = pd.read_sql(query, ENGINE)
    print(f"{args.class_name} : {len(df)}개")
    error_rows = []
    empty_crop_info = []
    bbox_dict = defaultdict(list)
    tmp_img_path = "tmp"
    for _, row in tqdm(df.iterrows(), total=len(df)):
        img_path = row['original_path'].replace("/data/", "/data3/")
        if tmp_img_path != img_path:
            tmp_img_path = img_path
            img_obj = cv2.imread(tmp_img_path)
            width, height, _ = img_obj.shape
        
        if row['crop_info'] is None:
            empty_crop_info.append(row)
        else :
            tmp_crop_info = row['crop_info'].replace("[", "").replace("]", "")
            tmp_crop_info = tmp_crop_info.split(", ")
            if len(tmp_crop_info) == 4:
                bbox = tmp_crop_info
            elif len(tmp_crop_info) == 5:
                bbox = tmp_crop_info[:4]
            else :
                error_rows.append(row)
                continue
        
        converted_bbox = convert_to_yolo_format(bbox, width, height)
        bbox_dict[img_path].append(converted_bbox)
    
    print("make bbox_dict Done\n")
    
    # save with txt
    
    # cnt = -1
    for img_path, bbox_list in tqdm(bbox_dict.items()):
        # cnt += 1
        # if cnt == 10:
        #     sys.exit(1)
        tmp_dir = os.path.dirname(img_path)
        tmp_filename = os.path.basename(img_path).split(".")[0]
        # save_path = os.path.join(args.save_dir, f"{tmp_filename}.txt")
        save_path = os.path.join(args.save_dir, f"{tmp_filename}.txt")
        
        with open(save_path, "w") as f:
            for bbox_value in bbox_list:
                line = f"{args.label} {' '.join(list(map(str, bbox_value)))} \n"
                f.write(line)
    print("Done")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--class_name", "-c", type=str, default="음식아님")
    parser.add_argument("--label", "-l", type=int, default=2)
    parser.add_argument("--save_dir", "-s", type=str, default="./test")
    parser.add_argument("--server", type=str, help="dev, main")
    args = parser.parse_args()
    
    if args.server == "dev":
        server_info = DevServer()
    else :
        server_info = MainServer()
    
    ENGINE = create_engine(f"mysql+pymysql://{server_info.DB_USERNAME}:{server_info.DB_PASSWORD}@{server_info.DB_HOST}/{server_info.DB_NAME}")
    
    main(args)