import glob
import os.path
import sys

from setuptools.config import read_configuration


if __name__ == "__main__":
    data_files = []
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
        "build_exe": {
            "excludes": [
                "test",
                "tkinter",
            ],
            "include_files": data_files,
        },
    }

    import cx_Freeze.hooks
    from cx_Freeze import setup, Executable
    del cx_Freeze.hooks.load__ctypes
    setup(
        executables=[
            Executable("pdl2pdf.py"),
        ],
        **cfg
    )
