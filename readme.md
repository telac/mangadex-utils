# about

a quick and dirty tool to download manga chapters from mangadex.

creates a quick .cbz archive of the downloaded contents as well.

# usage

download full release:

```
python ./mangadex_downloader.py --manga_id [mangadex_manga_id_goes_here] --path /path/to/output/folder
```

download specific chapters
```
python ./mangadex_downloader.py --manga_id [mangadex_manga_id_goes_here] --path /path/to/output/folder --start_chapter 67 --end_chapter 68
```
