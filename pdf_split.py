# -*- coding: utf-8 -*-
import PyPDF2
import easygui

def split_pdf(input_path, output_path_prefix,split_pages=[],split_num = 2):

    file_num = 1
    with open(input_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        
        

        # 分割するページ番号が与えられなかったときは、与えられた整数で等分する
        if len(split_pages) == 0:
            split_pages = [i for i in range(num_pages) if (((i+1)%(num_pages//split_num))==0)]
            
        for page_number in range(num_pages):
            if (page_number == 0) | (page_number in split_pages):
                writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[page_number])

            
            if ((page_number+1) in split_pages ) |(page_number == num_pages-1):
                output_path = f"{output_path_prefix}_{file_num}.pdf"
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                file_num += 1


if __name__ == '__main__':

    input_file_path = easygui.fileopenbox(title="分割したいPDFファイルを選んでください")
    output_file_path_prefix = easygui.enterbox("分割したPDFファイルを保存する名前を_枝番.pdf抜きで指定してください(フルパス)","保存ファイル名を指定")
    try:
        split_pages = [element for element in map(int,easygui.enterbox("分割したいページ番号をカンマ区切りで入力してください","分割するページの指定").split(","))]
        split_pdf(input_file_path, output_file_path_prefix,split_pages)
    except:
        split_num = int(input("PDFを分割したい個数を入力してください\n->"))
        split_pdf(input_file_path, output_file_path_prefix,split_num=split_num)