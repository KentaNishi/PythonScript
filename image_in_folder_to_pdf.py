# -*- coding: utf-8 -*-
from PIL import Image
from pathlib import Path
import re
import easygui
import os
import cv2

OUTPUT_DIR = "./generated_pdf/"

def extract_index(file_name):
    file_name = str(file_name)
    if file_name.__contains__("/"):
        file_name = file_name.split("/")[-1]
    elif file_name.__contains__("\\"):
        file_name = file_name.split("\\")[-1]
    regex = re.compile(r'[0-9]+')
    catches = re.findall(regex,file_name)
    return int(catches[-1])

def concatenate_images(image_list,multiples):
    output_image_list = []
    # 画像を結合するためのキャンバスを作成
    max_width = max(image.width for image in image_list)
    max_height = max(image.height for image in image_list)
    print(max_width,max_height)
    # 画像をキャンバス上に結合する
    for i,image in enumerate(image_list):
        x_offset = i % multiples[0]
        y_offset = (i // multiples[0] ) % multiples[1]
        if (x_offset == 0 and y_offset == 0):
            canvas = Image.new('RGB', (multiples[0]*max_width,multiples[1]*max_height))
        canvas.paste(image, (x_offset*max_width,y_offset*max_height))
        if (x_offset+1 == multiples[0] and y_offset+1 == multiples[1]):
            output_image_list.append(canvas)
    if not (x_offset+1 == multiples[0] and y_offset+1 == multiples[1]):
        output_image_list.append(canvas)
    return output_image_list

def convert_images2pdf(image_folder:str,multiples=(2,2)):

    # PDFファイルの保存先パス
    pdf_path = OUTPUT_DIR + os.path.splitext(os.path.basename(image_folder))[0] + ".pdf"
    merged_pdf_path = pdf_path[:-4] + "_merge.pdf"

    # 画像ファイルの拡張子
    image_extensions = [".jpg", ".jpeg", ".png"]

    # 画像ファイルのリストを取得
    image_files = sorted(Path(image_folder).glob("*"),key=extract_index)
    image_files = [f for f in image_files if f.suffix.lower() in image_extensions]

    # PDFを作成するためのイメージリスト
    image_list = []

    selcted_x_list = []
    selcted_y_list = []
    def _mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Selected coordinates: ({x}, {y})")
            selcted_x_list.append(x)
            selcted_y_list.append(y)
    #end func

    window_str = "Select upper left corner and lower right corner of target area and press 'q' to confirm"
    cv2.namedWindow(window_str, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_str, _mouse_callback)
    image = cv2.imread(str(image_files[0]))
    while True:
        cv2.imshow(window_str, image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    #end while

    h_min = min(selcted_y_list)
    h_max = max(selcted_y_list)
    w_min = min(selcted_x_list)
    w_max = max(selcted_x_list)

    # 画像を開いてイメージリストに追加
    for image_file in image_files:
        image = Image.open(image_file)
        image_list.append(image.crop((w_min,h_min,w_max,h_max)))

    # 最初の画像を基準にPDFを作成
    image_list[0].save(pdf_path, save_all=True, append_images=image_list[1:])
    concatenate_img_list = concatenate_images(image_list,multiples=multiples)
    concatenate_img_list[0].save(merged_pdf_path, save_all=True, append_images=concatenate_img_list[1:])
    print("PDF created successfully.")

if __name__ == '__main__':
    image_folder = easygui.diropenbox(title="pdfにまとめたい画像のあるフォルダを指定してください")
    try:
        multiples = [int(element) for element in easygui.enterbox("複数ページをまとめたい場合は横、縦の順で何枚並べるかカンマ区切りで設定してください。","複数ページをまとめる").split(",")]
    except:
        multiples = None
    if multiples == None:
        convert_images2pdf(image_folder)
    else:
        convert_images2pdf(image_folder,multiples)

