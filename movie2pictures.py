import sys
import cv2
import os

# 初期設定
try:
    defalut_movie_path = os.path.join(os.environ['INPUT_MOVIE_PATH'],'test.mp4')  # 動画ファイルのパス
    default_output_folder = os.path.join(os.environ['OUTPUT_PDF_PATH'],os.path.splitext(os.path.basename(defalut_movie_path))[0]) # 保存先フォルダ
except:
    defalut_movie_path = ""
    default_output_folder = ""
threshold = 0.008  # 



def movie2pictures(movie_path=defalut_movie_path,output_folder=default_output_folder,threshold = 0.008):
    """
    mp4ファイルから、フレーム間の差分をみて画像に分割する関数

    Input
        movie_path (str): 動画ファイルへのフルパス
        output_folder (str): 画像を出力するフォルダへのフルパス
        threshold (float): 差分の閾値 0~1 ,255✕3チャンネルでの差を最大値に対する割合で設定する。注目領域だけに限って差をとる
    Output
        None （ファイル生成のみで特に関数としての出力はない）
    """
    # 動画のキャプチャーを作成
    cap = cv2.VideoCapture(movie_path)

    # 最初のフレームを取得
    ret, prev_frame = cap.read()
    h,w,c=prev_frame.shape

    # 着目領域の選択
    # h_min = h//4
    # h_max = h//3*2
    # w_min = w//4
    # w_max = w//4*3
    selcted_x_list = []
    selcted_y_list = []
    def _mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Selected coordinates: ({x}, {y})")
            selcted_x_list.append(x)
            selcted_y_list.append(y)
    #end func

    window_str = "着目する矩形領域を左上、右下の順に左クリックで指定してください.終わったらキーボードでqを押してください。"
    cv2.namedWindow(window_str)
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

    # フレーム番号のカウンター
    frame_counter = 0



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
            if not os.path.isdir(output_folder):
                os.makedirs(output_folder)
            image_path = os.path.join(output_folder,f'frame_{frame_counter}.jpg')
            cv2.imwrite(image_path, frame)
            print(f'Saved image: {image_path}')
            
            # 現在のフレームを前のフレームとして保存
            prev_frame = frame.copy()
            # フレーム番号を更新
            frame_counter += 1

    # キャプチャーを解放
    cap.release()

if __name__ =='__main__':
    movie_path = input("動画へのフルパスを指定してください。\n->")
    output_folder = input("画像を出力するフォルダへのフルパスを指定してください。\n->")
    threshold = float(input("0~1の範囲でフレーム間差分を見るときの閾値を設定してください。\n 例：1%を想定しているときは0.01を入力\n->"))
    movie2pictures(movie_path,output_folder,threshold)