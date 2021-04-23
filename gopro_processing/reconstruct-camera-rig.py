import Metashape
from os import listdir
from os.path import isfile, join, isdir
import argparse

'''
./metashape.sh -platform offscreen -r ../process-scan.py /scratch/data/jmm403/ --full
aws s3 sync ./rapaura s3://tiles.joshm.cc/rapaura
'''

def get_images(directory):
    images = []
    for f in listdir(directory):
        if isfile(join(directory, f)) and f.lower().endswith("jpg"):
            images.append(join(directory, f))
            #print(join(directory, f))
    return images

def get_camera_array(directory):
    camera_folders = [f for f in listdir(directory) if isdir(join(directory, f))]
    camera_folders.sort()
    images = []
    for camera_folder in camera_folders:
        for path in get_images(join(directory, camera_folder)):
            images.append(path)
    print("Found %d images." %len(images))
    return images

#Parse arguments
parser = argparse.ArgumentParser(prog="Process Survey", description="Automation script meant to called by Metashape.")
parser.add_argument("path",
    help="Path to the root directory of the survey")

parser.add_argument('--full', action='store_true', help="Don't load a checkpoint, run each stage.")

parser.add_argument('--load', action='store_true', help="")
parser.add_argument('--photos', action='store_true', help="")
parser.add_argument('--cameras', action='store_true', help="")
parser.add_argument('--cloud', action='store_true', help="")
parser.add_argument('--dem', action='store_true', help="")
parser.add_argument('--ortho', action='store_true', help="")
parser.add_argument('--export-ortho', action='store_true', help="")
parser.add_argument('--export-dem', action='store_true', help="")
parser.add_argument('--export-dense', action='store_true', help="")
parser.add_argument('--export-cameras', action='store_true', help="")
parser.add_argument('--workitem', action='store', help="", type=int, default=20)


args = parser.parse_args()

#Set path variables
path = args.path
psx = "checkpoint.psx"

doc = Metashape.Document()

if args.full:
    stage_open = False
    stage_add_photos = True
    stage_align_cameras = True
    stage_dense_cloud = True
    stage_dem = True
    stage_ortho = True
    stage_ortho_export = True
    stage_dem_export = False #True
    stage_dense_export = False #True
    stage_export_cameras = False #True
else:
    stage_open = args.load
    stage_add_photos = args.photos
    stage_align_cameras = args.cameras
    stage_dense_cloud = args.cloud
    stage_dem = args.dem
    stage_ortho = args.ortho
    stage_ortho_export = args.export_ortho
    stage_dem_export = args.export_dem
    stage_dense_export = args.export_dense
    stage_export_cameras = args.export_cameras

if stage_open:
    doc.open(join(path, psx), ignore_lock=False)

if stage_add_photos:
    chunk = doc.addChunk()
    chunk.addPhotos(get_camera_array(path))
    doc.save(join(path, psx))

if stage_align_cameras:
    chunk = doc.chunk
    options = dict(#accuracy=Metashape.HighAccuracy,
        generic_preselection=True,
        reference_preselection=True,
        keypoint_limit=40000,
        tiepoint_limit=4000,
        filter_mask=True,
    )

    chunk.matchPhotos(**options)
    chunk.alignCameras(adaptive_fitting=True)
    doc.save(join(path, psx))

if stage_dense_cloud:
    chunk = doc.chunk
    chunk.buildDepthMaps(workitem_size_cameras=args.workitem, max_workgroup_size=args.workitem*5)
    chunk.buildDenseCloud()
    doc.save(join(path, psx))

if stage_dem:
    chunk = doc.chunk
    chunk.buildDem()
    doc.save(join(path, psx))

if stage_ortho:
    chunk = doc.chunk
    chunk.buildOrthomosaic(surface_data=Metashape.DataSource.ElevationData, workitem_size_cameras=args.workitem,max_workgroup_size=args.workitem*5)
    doc.save(join(path, psx))

if stage_ortho_export:
    chunk = doc.chunk
    chunk.exportOrthomosaic(join(path, "ortho.zip"),
    format=Metashape.RasterFormatTMS,
    image_format=Metashape.ImageFormatPNG)

if stage_dem_export:
    chunk = doc.chunk
    chunk.exportDem(join(path, "dem.zip"),
        format=Metashape.RasterFormatTMS,
        image_format=Metashape.ImageFormatPNG,
        raster_transform=Metashape.RasterTransformPalette)

if stage_dense_export:
    chunk = doc.chunk
    chunk.exportPoints(join(path, "dense.ply"),
        source=Metashape.DenseCloudData,
        format=Metashape.PointsFormatPLY)
    chunk.exportPoints(join(path, "dense.las"),
        source=Metashape.DenseCloudData,
        format=Metashape.PointsFormatLAS)

if stage_export_cameras:
    chunk = doc.chunk
    chunk.sensors[0].calibration.save(join(path, "opencv.xml"), "opencv")

