from zipfile import ZipFile
from glob import glob
import os
from pathlib import Path
import argparse


def to_cbz(filename, path):
    files = glob(path + '/' + '*.png')
    with ZipFile(f"{path}/{filename}", 'w') as zip_object:
        for f in files:
            print(f"adding file {f} to zip")
            zip_object.write(f, os.path.basename(f))

def folder_to_cbz(root):
    dirs = os.walk(root)
    for root, dirs, files in dirs:
        if files:
            series_name = os.path.basename(Path(root).parent)
            volume_name = os.path.basename(root)
            fname = f"{series_name}_{volume_name}.cbz"
            to_cbz(fname, root)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create .cbz files to be used by comic readers")
    parser.add_argument('--path', help="root folder of the volumes", required=True)
    args = parser.parse_args()
    folder_to_cbz(args.path)
    
