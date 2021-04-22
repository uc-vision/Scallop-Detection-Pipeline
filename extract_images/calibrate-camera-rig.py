import Metashape
from os import listdir
from os.path import isfile, isdir, join
import argparse
import json
import pathlib

def mkdir(directory):
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

def get_images(directory):
    images = []
    for f in listdir(directory):
        if isfile(join(directory, f)) and f.lower().endswith("jpg"):
            images.append(join(directory, f))
            #print(join(directory, f))
    images.sort()
    return images

def get_camera_array(directory):
    camera_folders = [f for f in listdir(directory) if isdir(join(directory, f))]
    camera_folders.sort()
    cameras = []
    for camera_folder in camera_folders:
        images = []
        for path in get_images(join(directory, camera_folder)):
            images.append({
                "path": path,
                "calibrate_with": False
            })

        camera = {
            "name": camera_folder,
            "directory": join(directory, camera_folder),
            "images":  images
        }
        cameras.append(camera)
    
    return cameras

#Parse arguments
parser = argparse.ArgumentParser(prog="calibrate-camera-rig", description="Calibrates multiple cameras.")
parser.add_argument("path",
    help="Path to the root directory of the survey")

args = parser.parse_args()

#Set path variables
path = args.path
output_dir = path+ "_processed"
mkdir(output_dir)

camera_array = get_camera_array(path)

for camera in camera_array:
    for image in camera["images"][4:]:
        image["calibrate_with"] = True


for camera in camera_array:
    camera["calibration_file"] = join(output_dir,camera["name"]+".xml")

    doc = Metashape.Document()

    chunk = doc.addChunk()
    images = [image["path"] for image in camera["images"] if image["calibrate_with"]]
    print(images)

    chunk.addPhotos(images)

    options = dict(
        generic_preselection=True,
        reference_preselection=True,
        keypoint_limit=40000,
        tiepoint_limit=4000,
        filter_mask=True,
    )

    chunk.matchPhotos(**options)
    chunk.alignCameras(adaptive_fitting=True)
    chunk.sensors[0].calibration.save(camera["calibration_file"], Metashape.CalibrationFormatOpenCV)

    camera["calibration"] = {
        "width": chunk.sensors[0].calibration.width,
        "height": chunk.sensors[0].calibration.height,
        "b1": chunk.sensors[0].calibration.b1,
        "b2": chunk.sensors[0].calibration.b2,
        "cx": chunk.sensors[0].calibration.cx,
        "cy": chunk.sensors[0].calibration.cy,
        "f": chunk.sensors[0].calibration.f,
        "k1": chunk.sensors[0].calibration.k1,
        "k2": chunk.sensors[0].calibration.k2,
        "k3": chunk.sensors[0].calibration.k3,
        "k4": chunk.sensors[0].calibration.k4,
        "p1": chunk.sensors[0].calibration.p1,
        "p2": chunk.sensors[0].calibration.p2,
        "p3": chunk.sensors[0].calibration.p3,
        "p4": chunk.sensors[0].calibration.p4
    }

with open(join(output_dir, "camera_array.json"), "w") as json_out:
    json_out.write(json.dumps(camera_array, indent=2))




