# -*- coding: utf-8 -*-
from cx_Freeze import setup, Executable

# アイコンファイルのパス
icon = 'icons/eiga_film.ico'

options = {
    "build_exe": {
        "packages": ["numpy","cv2","easygui"],
        'include_files': ["icons/"]
    }
}

exe = Executable(script="movie2pictures.py",
                 icon=icon)

setup(
    name="movie2pic",
    version="1.0",
    description="extract images from movie based on difference between frames",
    options=options,
    executables=[exe]
)