# -*- coding: utf-8 -*-
import cv2
import os
import easygui

# 初期設定
try:
    defalut_movie_path = os.path.join(os.environ['INPUT_MOVIE_PATH'],'test.mp4')  # 動画ファイルのパス
    default_output_folder = os.path.join(os.environ['OUTPUT_PDF_PATH'],os.path.splitext(os.path.basename(defalut_movie_path))[0]) # 保存先フォルダ
except:
    defalut_movie_path = ""
    default_output_folder = ""
threshold = 0.008  # 



def movie2pictures(movie_path=defalut_movie_path,output_base_folder=default_output_folder,threshold = 0.008):
    """
    mp4ファイルから、フレーム間の差分をみて画像に分割する関数

    Input
        movie_path (str): 動画ファイルへのフルパス
        output_folder (str): 画像を出力するフォルダへのフルパス
        threshold (float): 差分の閾値 0~1 ,255✕3チャンネルでの差を最大値に対する割合で設定する。注目領域だけに限って差をとる
    Output
        None （ファイル生成のみで特に関数としての出力はない）
    """

    #出力フォルダを設定
    output_folder = os.path.join(output_base_folder,os.path.splitext(os.path.basename(movie_path))[0])
    # フォルダが存在していない場合は作成
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    
    # 動画のキャプチャーを作成
    cap = cv2.VideoCapture(movie_path)

    # 最初のフレームを取得
    ret, prev_frame = cap.read()
    h,w,c=prev_frame.shape
    # フレーム番号のカウンター
    frame_counter = 0
    image_path = os.path.join(output_folder,f'frame_{frame_counter}.jpg')
    cv2.imwrite(image_path, prev_frame)
    frame_counter += 1

    # 着目領域の選択
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

    while True:
        cv2.imshow(window_str, prev_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    #end while

    h_min = min(selcted_y_list)
    h_max = max(selcted_y_list)
    w_min = min(selcted_x_list)
    w_max = max(selcted_x_list)
    max_diff = (h_max-h_min)*(w_max-w_min)*3*255

    

    while True:
        # フレームを取得
        ret, frame = cap.read()

        # 動画の終了条件（フレームが取得できなかった場合）
        if not ret:
            break

        # フレーム差分の計算
        diff    = cv2.absdiff(prev_frame[h_min:h_max,w_min:w_max,:], frame[h_min:h_max,w_min:w_max,:]) 

        # 差分が閾値を超えるかどうかを確認
        diff_sum = diff.sum()
        if diff_sum/max_diff > threshold:
            # 画像を保存
            
            
            image_path = os.path.join(output_folder,f'frame_{frame_counter}.jpg')
            cv2.imwrite(image_path, frame)
            print(f'Saved image: {image_path}')
            
            # 現在のフレームを前のフレームとして保存
            prev_frame = frame.copy()
            # フレーム番号を更新
            frame_counter += 1

    # キャプチャーを解放
    cap.release()
    
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
    movie_path = easygui.fileopenbox(title="入力する動画ファイルを選択してください。")
    output_folder = easygui.diropenbox(title="画像を出力するフォルダを選択してください。")
    threshold = floatbox("0~1の範囲でフレーム間差分を見るときの閾値を設定してください。", "Number Input",default=0.01,lowerbound=0.0001,upperbound=0.99)
    movie2pictures(movie_path,output_folder,threshold)