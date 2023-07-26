import re
import os
import shutil
import argparse
import json


def rename_files(folder_path,pattern,replacement,is_copy=True):
    """
    指定したフォルダ内のファイル名を一括で変更します。

    Parameters:
        folder_path (str): フォルダのパス
        pattern (str): 正規表現パターン。このパターンに一致するファイル名を検索します。
        replacement (str): 置換文字列。一致した部分をこの文字列に置換します。
        is_copy (bool, optional): Trueの場合はファイルをコピーして新しい名前に変更します。Falseの場合はファイル名を直接変更します。デフォルトはTrue。

    Returns:
        None

    Notes:
        フォルダ内のファイル名が指定した正規表現パターンに一致する場合、その部分を置換文字列で置換して新しいファイル名を作成します。
        is_copyがTrueの場合はファイルをコピーして新しい名前に変更します。is_copyがFalseの場合はファイル名を直接変更します。
    """
    # フォルダ内のファイル名を取得
    file_list = os.listdir(folder_path)

    # 正規表現に一致するファイル名を変更
    for filename in file_list:
        if re.search(pattern, filename):
            new_filename = re.sub(pattern, replacement, filename)
            src = os.path.join(folder_path, filename)
            dst = os.path.join(folder_path, new_filename)

            if is_copy:
                shutil.copy(src, dst)
                print(f"{filename} を {new_filename} に変更しました。元のファイルは残っています")
            else:
                os.rename(src, dst)
                print(f"{filename} を {new_filename} に変更しました。")

def load_replacement_json_dict():
    base_path = os.environ.get('OBSIDIAN_PATH')
    with open(base_path+"data.json", "r",encoding='utf-8') as file:
        loaded_data = json.load(file)
    return_dict = dict(zip(map(lambda x: os.path.join(os.environ['OBSIDIAN_PATH'],x),loaded_data.keys()),loaded_data.values()))
    return return_dict

def copy_imgs_by_json():
    for key,value in load_replacement_json_dict().items():
        shutil.copy(key,value)

if __name__ == "__main__":
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="フォルダ内のファイル名を正規表現で一括変更するプログラム")
    parser.add_argument("-f","--folder_path", help="対象のフォルダパス")
    parser.add_argument("-p","--pattern", help="置換したい正規表現パターン")
    parser.add_argument("-r","--replacement", help="置換後の文字列")
    parser.add_argument("-c","--copy",action="store_true", help="コピーするか、置き換えるかのフラグ")
    args = parser.parse_args()

    # フォルダ内のファイル名を正規表現で一括変更
    rename_files(args.folder_path, args.pattern, args.replacement,args.copy)