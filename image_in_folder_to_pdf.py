# -*- coding: utf-8 -*-
from PIL import Image
from pathlib import Path
import re

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
        print(x_offset,y_offset)
        if (x_offset == 0 and y_offset == 0):
            canvas = Image.new('RGB', (multiples[0]*max_width,multiples[1]*max_height))
        canvas.paste(image, (x_offset*max_width,y_offset*max_height))
        if (x_offset+1 == multiples[0] and y_offset+1 == multiples[1]):
            output_image_list.append(canvas)
    if not (x_offset+1 == multiples[0] and y_offset+1 == multiples[1]):
        output_image_list.append(canvas)
    return output_image_list

def convert_images2pdf(image_folder:str):

    # PDFファイルの保存先パス
    pdf_path = OUTPUT_DIR + image_folder.split("/")[-1] + ".pdf"
    merged_pdf_path = OUTPUT_DIR + image_folder.split("/")[-1] + "_merge.pdf"

    # 画像ファイルの拡張子
    image_extensions = [".jpg", ".jpeg", ".png"]

    # 画像ファイルのリストを取得
    image_files = sorted(Path(image_folder).glob("*"),key=extract_index)
    image_files = [f for f in image_files if f.suffix.lower() in image_extensions]

    # PDFを作成するためのイメージリスト
    image_list = []

    # 画像を開いてイメージリストに追加
    for image_file in image_files:
        image = Image.open(image_file)
        w,h = image.size
        image_list.append(image.crop((w//4+100,100,w//4*3,h-100)))

    # 最初の画像を基準にPDFを作成
    image_list[0].save(pdf_path, save_all=True, append_images=image_list[1:])
    concatenate_img_list = concatenate_images(image_list,multiples=(2,2))
    print(len(image_list),len(concatenate_img_list))
    concatenate_img_list[0].save(merged_pdf_path, save_all=True, append_images=concatenate_img_list[1:])
    print("PDF created successfully.")

if __name__ == '__main__':
    image_folder = input("pdfにまとめたい画像のあるフォルダを指定してください. 階層は/で区切ってください。\n->")
    convert_images2pdf(image_folder)

