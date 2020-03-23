from setuptools.config import read_configuration


if __name__ == "__main__":
    cfg = read_configuration("setup.cfg")
    # perhaps use cfg["options"]["packages"]?
    cfg = cfg["metadata"]
    cfg["options"] = {
        "build_exe": {
            "excludes": [
                "test",
                "tkinter",
            ],
        },
    }

    from cx_Freeze import setup, Executable
    setup(
        executables=[
            Executable("pdl2pdf.py"),
        ],
        **cfg
    )
