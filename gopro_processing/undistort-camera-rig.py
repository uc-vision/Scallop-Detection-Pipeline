from os import listdir
from os.path import isfile, isdir, join, basename
import argparse
import json
import pathlib
import cv2
from types import SimpleNamespace
import numpy as np
from tqdm import tqdm

def mkdir(directory):
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

def get_camera_parameters(camera):
    c = SimpleNamespace(**camera["calibration"])
    K = np.array([
        [c.f + c.b1,    c.b2,   c.cx + c.width / 2], 
        [0,             c.f,    c.cy + c.height / 2], 
        [0,             0,      1]
    ])
    
    dist= np.array([[c.k1, c.k2, c.p2, c.p1, c.k3]])
    return K, dist

def get_optimal_camera_matrix(camera):
    mtx, dist = get_camera_parameters(camera)
    c = SimpleNamespace(**camera["calibration"])
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (c.width,c.height), 1, (c.width,c.height))
    return newcameramtx, roi


#Parse arguments
parser = argparse.ArgumentParser(
    prog="undistort-camera-rig", 
    description="Uses previously created camera calibrations to undistort multiple cameras to a comon projection.")
parser.add_argument("path",
    help="Path to the calibration output")

args = parser.parse_args()

#Set path variables
path = args.path

with open(join(path, "camera_array.json"), "r") as camera_array_file:
    camera_array = json.loads(camera_array_file.read())



target_mtx, target_roi = get_optimal_camera_matrix(camera_array[0])

for camera in camera_array:

    image_out_dir = join(path, camera["name"])
    mkdir(image_out_dir)

    mtx, dist = get_camera_parameters(camera)
    print(dist)
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, target_mtx, 
        (camera["calibration"]["width"],camera["calibration"]["height"]), 
        5)

    for image in tqdm(camera["images"]):
        img = cv2.imread(image["path"])
        dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
        x, y, w, h = target_roi
        dst = dst[y:y+h, x:x+w]

        output_image_path = join(image_out_dir, basename(image["path"]))

        cv2.imwrite(output_image_path, dst)
