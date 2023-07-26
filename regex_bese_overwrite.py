# -*- coding: utf-8 -*-
import re
import glob
import os
import json

def recursive_file_search(file_list,path,extension=""):
    """
    指定したパスから再帰的にファイルを検索します。

    Parameters:
        file_list (list): ファイルパスを格納するリスト。
        path (str): 検索を開始するパス。
        extension (str, optional): ファイルの拡張子を指定するオプション。デフォルトは空文字列。

    Returns:
        list: 検索結果として得られたファイルパスを格納したリスト。

    Notes:
        指定したパスから再帰的にファイルを検索し、file_listにファイルパスを追加します。
        デフォルトでは、extensionが空文字列の場合はすべてのファイルを検索し、extensionが指定されている場合はその拡張子に一致するファイルのみを検索します。
    """
    candidates = os.listdir(path)
    for candidate in candidates:
        tgt_path = os.path.join(path,candidate)
        if os.path.isdir(tgt_path):
            file_list = recursive_file_search(file_list,tgt_path,extension)
        else:
            if extension=="":
                file_list.append(tgt_path)
            elif candidate.endswith(extension):
                file_list.append(tgt_path)
            else:
                pass
            #endif        
        #endif
    #endfor
    return file_list

def split_by_any_directory_delimiter(text):
    # 正規表現パターンを作成
    delimiters = ['/','\\']
    pattern = '|'.join(map(re.escape, delimiters))
    
    # 文字列を分割
    result = [element for element in re.split(pattern, text) if len(element)>0]
    return result

def path_replacement(original_text,path_prefix):
    path_elements = split_by_any_directory_delimiter(original_text)
    index = path_elements.index('03_Extra')
    path = '/'.join([path_prefix]+path_elements[index+1:])
    return path

def create_replacement_dict(text, pattern,path_prefix):
    replacement_dict = {}
    for match in re.finditer(pattern, text):
        original_text = match.group()
        replacement_text = path_replacement(original_text,path_prefix)  # 置換後の文字列をここで指定
        replacement_dict.setdefault(original_text,replacement_text)

    return replacement_dict

def replace_text_with_regex(input_file, output_file,output_base_folder,pattern=""):
    """
    正規表現を使ってテキストファイル内の特定のパターンを書き換える関数

    Parameters:
        input_file (str): 入力ファイルのパス
        output_file (str): 出力ファイルのパス
        pattern (str): 置換したい文字列の正規表現パターン
    Returns:
        image_path_dict (dict) : 画像ファイル関連の文字列を置換したときに、置換前後を確認するための辞書

    Examples:
        replace_text_with_regex("input.txt", "output.txt", r"\d+", "NUM")
        # input.txtの中で数字に一致する箇所をすべて"NUM"に置換し、output.txtに保存する
    """

    # obsidian関係の正規表現、置換の関係上、上から順に使います
    embedded_wiki_link_pattern = r'!\[\[[^\.]*?\]\]' # 後で”！”と括弧を取り外して使う、wikiリンクより先に使う必要がある。
    wiki_link_pattern = r'\[\[[^\.]*?\]\]'  # あとで括弧を取り外して使う
    ping_file_pattern = r"[^!\[\]\(\)]*?\.png" #画像ファイル周りのリンクを貼っているところから、ファイルのパスを取得
    front_matter_pattern = r"---\n([\s\S]+?)\n---" # フロントマターをhugoの内容にあるように変更
    

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    
    # patternが与えられなかったときはObsidianからhugoの変換とみて、ファイルの書き換えを行う
    if len(pattern) == 0:
        #ヘッダー部分から改行してすぐに特殊文字を使うとあまり認識がうまく行かないので、改行を一つ追加する
        for match in re.finditer(r'#+ .*\n',content):
            original_match_text = match.group()
            content = content.replace(original_match_text,original_match_text+"\n")
        #インライン以外の数式表記が文字と連続すると、認識がうまく行かないので、改行を追加する
        for match in re.finditer(r'[ぁ-んァ-ヶー一-龯。]\n{0,1}\$\$',content):
            original_match_text = match.group()
            content = content.replace(original_match_text,original_match_text[:-2]+"\n\n$$")
        #数式表記が連続すると、認識がうまく行かないので、改行を追加する
        content =  re.sub(r'\$\$\n{0,1}\$\$','$$\n\n$$',content)
        
        # 記事埋め込みリンクの部分をリンク先ファイルの内容で置換,置換した後にマッチが変わる可能性があるので、埋め込みwikiリンクが見つからなくなるまで実行
        cnt = 0 # 無限ループを避けるために設定
        while(not (re.search(embedded_wiki_link_pattern, content)==None)):
            if cnt > 10:
                break
            for match in re.finditer(embedded_wiki_link_pattern, content):
                original_match_text = match.group()
                match_text = re.sub(r'[!\[\]]','',original_match_text) # 括弧と!マークを除く
                #　同一ファイル内の埋め込みのときはそこへのリンクだけおいて次のループに行く
                if match_text.startswith('#'):
                    tgt_content = f"[{match_text[1:]}]({match_text})"
                else:
                    match_text_elements = match_text.split("#")
                    tgt_file_name = match_text_elements[0] + ".md"
                    try:
                        tgt_file = recursive_file_search([],os.environ['OBSIDIAN_PATH'],tgt_file_name)[0]
                        with open(tgt_file, 'r', encoding='utf-8') as f:
                            tgt_content = f.read()
                        # 読み込むファイルのフロントマターは邪魔なので削除
                        tgt_content = re.sub(front_matter_pattern,"",tgt_content)
                        # ヘッダーまで指定しているとき
                        if len(match_text_elements) == 2:
                            # 該当のヘッダーを検索
                            tgt_match_text = re.search(r'#+ '+match_text_elements[1]).group()
                            # ヘッダーの終わりから、該当ヘッダーと同じレベルのヘッダーが見つかるまでを対象として抽出
                            start_index = tgt_content.find(tgt_match_text) + len(tgt_match_text)
                            header_level = len(tgt_match_text.split(" ")[0])
                            header_pattern = r'\n#{1,' + str(header_level) + '} '
                            end_index = start_index + re.search(header_pattern,tgt_content[start_index:]).span()[0]
                            tgt_content = tgt_content[start_index:end_index]
                    except:
                        continue
                content = content.replace(original_match_text,tgt_content)
            cnt += 1
    

        # wikiリンクをデプロイ後のリンクに変更、hugoのconfig.tomlにも依存する。ベースリンク/拡張子を除いたファイル名になるようにしている。
        for match in re.finditer(wiki_link_pattern, content):
            original_match_text = match.group()
            match_text = re.sub(r'[\[\]]','',original_match_text) # 括弧を除く
            match_text_element = match_text.split("#")
            # 該当箇所が＃から始まるときは、同じ記事内のリンクをつけるために、空になっている0番目の要素を拡張子を除いたファイル名に変更する
            if match_text_element[0] == '':
                tgt_content = f"[{match_text_element[-1]}](#{match_text_element[-1]})"
            else:
                url = os.environ['HUGO_BASE_URL'] + '/'.join(match_text_element)
                tgt_content = f'[{match_text_element[-1]}]({url})'
            content = content.replace(original_match_text,tgt_content)

    
        # 正規表現パターンに一致する文字列をreplacementで置換して、画像リンクを変更
        image_path_dict = create_replacement_dict(content, ping_file_pattern,'/'.join(split_by_any_directory_delimiter(output_base_folder)[:-2]+['static/img']))
        for key,value in image_path_dict.items():
            file_name = os.path.basename(value)
            content = content.replace('![['+key+']]','![/img/'+file_name+'](/img/'+file_name+')')
        
        #フロントマター部分の変更
        match = re.search(front_matter_pattern,content)
        original_front_matter = match.group()
        date_match = re.search(r'\d{4}-\d{2}-\d{2}',original_front_matter)
        front_matter_list = ['---','---']
        front_matter_list.insert(1,'title: ' + '"'+os.path.basename(output_file).split(".")[0]+'"')
        front_matter_list.insert(2,'date: ' + '"'+date_match.group() + "T00:00:00+09:00" +'"')
        front_matter_list.insert(3,'tags:\n- obsidian_note')
        front_matter_list.insert(4,'categories:\n- ' + split_by_any_directory_delimiter(os.path.dirname(output_file))[-1])
        content = "\n".join(front_matter_list) + content[len(original_front_matter)-1:]
    else:
        for match in re.finditer(pattern,content):
            original_match_text = match.group()
            replacement = "REPLACEMENT" #ここは適宜変えたいルールに従って作成
            content = content.replace(original_match_text,replacement)
    #endif
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return image_path_dict

def overwrite_files(base_path,folder_name,output_folder_name,extension):
    file_list = recursive_file_search([],base_path+folder_name,extension)
    replacement_dict = {}
    for file in file_list:
        rel_path = os.path.relpath(file,base_path+folder_name)
        output_base_folder = base_path+output_folder_name
        output_file = os.path.join(output_base_folder,rel_path)
        output_folder = os.path.dirname(output_file)
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        replacement_dict.update(replace_text_with_regex(file, output_file,output_base_folder))
    
    with open(base_path+"/image_path.json","w",encoding='utf-8') as f:
        json.dump(replacement_dict,f)

if __name__ == '__main__':
    base_path = os.environ.get('OBSIDIAN_PATH')
    folder_name = "08_project"
    output_folder_name = "SubVault/hugo_site_home/content/posts"
    extension = "md"
    overwrite_files(base_path,folder_name,output_folder_name,extension)