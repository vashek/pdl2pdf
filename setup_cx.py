import glob
import os
import os.path
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from typing import List, Tuple, Union

from setuptools.config import read_configuration  # type: ignore

GHOSTPCL_ZIP_URL = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs9550/ghostpcl-9.55.0-win64.zip"
GHOSTSCRIPT_EXE_URL = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs9550/gs9550w64.exe"
GHOSTSCRIPT_INSTALL_DIR = r"c:\Program Files\gs\gs9.55.0"
ENGLISH_TESSDATA_URL = "https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata"
DOWNLOAD_CACHE_DIR = ".download_cache"


def download(url, dest_path=DOWNLOAD_CACHE_DIR):
    os.makedirs(dest_path, exist_ok=True)
    parsed = urllib.parse.urlparse(url)
    fn = parsed.path.split("/")[-1]
    full_fn = os.path.join(dest_path, fn)
    if (os.path.isfile(full_fn) and os.stat(full_fn).st_size == 0) or not os.path.exists(full_fn):
        print(f"Downloading {url} to {full_fn}")
        fn_incomplete = full_fn + ".incomplete"
        with open(fn_incomplete, "wb") as f:
            try:
                with urllib.request.urlopen(url) as u:
                    while True:
                        data = u.read(65536)
                        if not data:
                            break
                        f.write(data)
            except urllib.error.HTTPError as e:
                print("Got HTTP error:\n" + e.read().decode("iso-8859-1"))
                raise
        os.rename(fn_incomplete, full_fn)
    else:
        print(f"{url} was already downloaded in {full_fn}")
    return full_fn


if __name__ == "__main__":
    gpcl_zip_fn = download(GHOSTPCL_ZIP_URL)
    gs_exe_fn = download(GHOSTSCRIPT_EXE_URL)
    eng_tessdata_fn = download(ENGLISH_TESSDATA_URL)

    if os.path.isdir(GHOSTSCRIPT_INSTALL_DIR):
        print(f"Found Ghostscript installed in {GHOSTSCRIPT_INSTALL_DIR}")
    else:
        print(f"Please install {gs_exe_fn} into {GHOSTSCRIPT_INSTALL_DIR}")
        sys.exit(1)

    gpcl_dir_object = tempfile.TemporaryDirectory()
    gpcl_dir = gpcl_dir_object.name
    with zipfile.ZipFile(gpcl_zip_fn) as gpcl_zip:
        for file_info in gpcl_zip.infolist():
            base_name = os.path.basename(file_info.filename)
            if file_info.is_dir() or not base_name or not file_info.filename or file_info.filename[-1:] in "\\/":
                continue
            print(f"extracting {file_info.filename}")
            with open(os.path.join(gpcl_dir, base_name), "wb") as f:
                f.write(gpcl_zip.read(file_info))

    data_files: List[Union[str, Tuple[str, str]]] = [
        # gpcl_zip_fn,
        # gs_exe_fn,
        (f"{GHOSTSCRIPT_INSTALL_DIR}/bin", r"gs\bin"),
        (f"{GHOSTSCRIPT_INSTALL_DIR}/iccprofiles", r"gs\iccprofiles"),
        (f"{GHOSTSCRIPT_INSTALL_DIR}/lib", r"gs\lib"),
        (f"{GHOSTSCRIPT_INSTALL_DIR}/Resource", r"gs\Resource"),
        (gpcl_dir, r"gpcl"),
        (eng_tessdata_fn, r"tessdata\eng.traineddata"),
    ]

    for dll_mask in ["libcrypto-*.dll", "libssl-*.dll", "libffi-7.dll"]:
        for dir_name in sys.path:
            found_dlls = glob.glob(os.path.join(dir_name, dll_mask))
            if found_dlls:
                data_files.append(sorted(found_dlls)[-1])
                print(f"... {data_files[-1]} found ...")
                break
        else:
            print(f"!!! {dll_mask} not found !!!")

    cfg = read_configuration("setup.cfg")
    # perhaps use cfg["options"]["packages"]?
    cfg = cfg["metadata"]
    cfg["options"] = {
        "build_exe": {"excludes": ["test", "tkinter"], "include_files": data_files},
        "install": {"prefix": cfg["name"]},
        "bdist_msi": {"initial_target_dir": f"C:\\SafeQ6\\" + cfg["name"]},
    }

    import cx_Freeze.hooks  # type: ignore
    from cx_Freeze import setup, Executable  # type: ignore

    del cx_Freeze.hooks.load__ctypes
    setup(executables=[Executable("pdl2pdf.py")], **cfg)
