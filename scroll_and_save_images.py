# -*- coding: utf-8 -*-
import os
import easygui
import pyautogui
from PIL import ImageGrab, ImageChops
from pynput import mouse
import time



def scroll_and_save_images(save_folder,folder_name,threshold = 0.99):
    """
    画面をクリックで指定してからEscで確定し、キーダウンでスクロールしながら指定領域のスクリーンショットを連続でおこなう関数
    画面はプライマリモニター以外を指定するとスクショがうまく行かないので、取りたいものをプライマリモニターに移るように移動させてください。
    Input
        save_folder (str): 保存先のベースパス、このフォルダの直下に後ほど入力するフォルダ名で新しいフォルダが作られる
        folder_name (str):フォルダ名
        threshold (float): 差分の閾値 0~1 ,255✕3チャンネルでの差を最大値に対する割合で設定する.完全一致じゃなければ保存するので0.99とか大きい値で良い.
        動的サイトとかで微妙に変わるときは要調整
    Output
        None （ファイル生成のみで特に関数としての出力はない）
    """

    #出力フォルダを設定
    output_folder = os.path.join(save_folder,folder_name)
    # フォルダが存在していない場合は作成
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    

    # 着目領域の選択
    selcted_x_list = []
    selcted_y_list = []
    break_flg = False
    #マウスイベントハンドラを定義
    def on_move(x, y):
        return

    def on_click(x, y, button, pressed):
        if pressed:
            selcted_x_list.append(x)
            selcted_y_list.append(y)
            # Stop listener
            return False

    def on_scroll(x, y, dx, dy):
        return

    # マウスのリスナーを起動,2箇所クリックしたら抜ける
    while True:
        with mouse.Listener(
                on_move=on_move,
                on_click=on_click,
                on_scroll=on_scroll) as listener:
            listener.join()
        
        if len(selcted_x_list) >= 2:
            h_min = min(selcted_y_list)
            h_max = max(selcted_y_list)
            w_min = min(selcted_x_list)
            w_max = max(selcted_x_list)

            print(h_min,h_max,w_min,w_max)
            break

    # 指定領域のスクショを取得
    image = ImageGrab.grab(bbox=(w_min,h_min,w_max,h_max))
    # フレーム番号のカウンターを設定
    frame_counter = 0
    # 画像を保存
    image_path = os.path.join(output_folder,f'frame_{frame_counter}.jpg')
    image.save(image_path)
    frame_counter += 1
    prev_image = image.copy()

    while True:
        
        # スクロール
        pyautogui.press("pagedown")
        #pyautogui.typewrite(' ')
        time.sleep(1)
        # スクショを取得
        image = ImageGrab.grab(bbox=(w_min,h_min,w_max,h_max))

        # 差分の計算
        diff    = ImageChops.difference(image, prev_image)
        # pixelレベルで違いがあるか否かを2値で判定して類似度を出す
        diff_pixels = diff.getdata()
        diff_amount = sum(pixel != (0, 0, 0) for pixel in diff_pixels)
        image_similarity = 1 - (diff_amount / (image.size[0] * image.size[1]))

        # 類似度が閾値を超えるかどうかを確認
        if image_similarity > threshold:
            break
        # 画像を保存
        image_path = os.path.join(output_folder,f'frame_{frame_counter}.jpg')
        image.save(image_path)
        print(f"save_image:{image_path}")
        # 現在のフレームを前のフレームとして保存
        prev_image = image.copy()
        # フレーム番号を更新
        frame_counter += 1
    
def floatbox(message,title,default,lowerbound=0.0,upperbound=1000000):
    try:
        value = float(easygui.enterbox(message,title))
    except:
        value = default
    finally:
        pass
    #endtry
    value = max(min(value, upperbound), lowerbound)
    return value



if __name__ =='__main__':
    save_folder = easygui.diropenbox(title="画像を出力するフォルダを選択してください。")
    folder_name = easygui.enterbox("フォルダ名を入力してください","フォルダ名の設定")
    threshold = floatbox("0~1の範囲でフレーム間差分を見るときの閾値を設定してください。", "Number Input",default=0.01,lowerbound=0.0001,upperbound=0.99)
    scroll_and_save_images(save_folder,folder_name,threshold)