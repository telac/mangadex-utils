from zipfile import ZipFile
from glob import glob
import os
from pathlib import Path
import argparse
import logging

def get_files(path):
    png_files = glob(path + '/' + '*.png')
    jpg_files = glob(path + '/' + '*.jpg')
    files = png_files + jpg_files
    return files

def get_partial_files(path, glob_expr):
    files = get_files(path)
    partial_files = []
    glob_expr = set(glob_expr)
    for file in files:
        basename = os.path.basename(file)
        if basename in glob_expr:
            partial_files.append(file)
    return partial_files

def to_chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def to_cbz(filename, path):
    files = get_files(path)
    with ZipFile(f"{path}/{filename}", 'w') as zip_object:
        for f in files:
            logging.debug(f"adding file {f} to zip")
            zip_object.write(f, os.path.basename(f))
        print(f"created CBZ archive at: {path}/{filename}")

def files_to_cbz(filename, glob_expr, path):
    files = get_partial_files(path, glob_expr)
    with ZipFile(f"{path}/{filename}", 'w') as zip_object:
        for f in files:
            logging.debug(f"adding file {f} to zip")
            zip_object.write(f, os.path.basename(f))
        print(f"created CBZ archive at: {path}/{filename}")

def get_chapters(files):
    chapters = set()
    for file in files:
        try:
            chapter = file.split("_")[0]
            float(chapter)
            chapters.add(chapter)
        except ValueError:
            continue
    return sorted(chapters, key= lambda x: float(x))

def merge_lists(d):
    l = []
    for key in d:
        l = l + d[key]
    return l
    
def folder_to_cbz(root):
    dirs = os.walk(root)
    for root, dirs, files in dirs:
        if files:
            chapters = get_chapters(files)
            if len(chapters) > 10:
                chunks = to_chunks(chapters, 10)
                for chunk in chunks:
                    chunk_file_dict = {volume:[] for volume in chunk}
                    for _file in files:
                        volume = _file.split("_")[0]
                        if volume in chunk_file_dict:
                            chunk_file_dict[volume].append(_file)
                    series_name = os.path.basename(Path(root).parent)
                    volume_name = os.path.basename(root)
                    chapter_min = float(min(chunk))
                    chapter_max = float(max(chunk))
                    fname = f"{series_name}_{volume_name}_c{chapter_min}_{chapter_max}.cbz"
                    merged_files = merge_lists(chunk_file_dict)
                    files_to_cbz(fname, merged_files, root)
            else:
                series_name = os.path.basename(Path(root).parent)
                volume_name = os.path.basename(root)
                fname = f"{series_name}_{volume_name}.cbz"
                
                to_cbz(fname, root)

def batch_rename(path):
    dirs = os.walk(path)
    for root, dirs, files in dirs:
        if files:
            files_to_be_renamed = get_files(root)
            for file in files_to_be_renamed:
                print(file)
                print(os.path.basename(file))
                volume = os.path.basename(file).split("_")[0]
                chapter = os.path.basename(file).split("_")[1]
                chapter, filetype = chapter.split(".")
                new_basename = f'{volume.zfill(5)}_{chapter.zfill(5)}.{filetype}'
                os.rename(file, f"{root}/{new_basename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create .cbz files to be used by comic readers")
    parser.add_argument('--path', help="root folder of the volumes", required=True)
    args = parser.parse_args()
    #batch_rename(args.path)
    folder_to_cbz(args.path)
    
