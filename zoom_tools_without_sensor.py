# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pyvirtualcam


def main():
    global cam
    with pyvirtualcam.Camera(848, 480, 30) as  cam:
        img_processing()

        print("program all finished")


def menu():
    print("------------------------------------How to use------------------------------------")
    print("enter: rec/rec stop       space: play/play stop     Tab: freeze      escape: exit")
    line()

def line():
    print("---------------------------------------------------------------------------------")

def sendframe(frame):
    
    cam.send(frame)
    cam.sleep_until_next_frame()


def show_original():
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    cv2.imshow('original', img)

def play(rec):
    print("playing...")
    j = 0
    t_freeze = 1000

    cv2.waitKey(t_freeze) #録画への切り替えのフリーズ1s（通信不良を装う）
    while cv2.waitKey(15) != 32: #エンターキーを押すと再生終了
        sendframe(rec[j]) #仮想カメラに出力
        j += 1
        if j == len(rec):
            j = 0
        
        show_original()


    cv2.waitKey(t_freeze)#録画からの切り替えのフリーズ1s（通信不良を装う）

    print("stop playing")
    menu()


def img_processing():

    global cap
    cap = cv2.VideoCapture(1) #カメラから画像を読み込み
    rec = [] #動画の一時保存先
    
    max_frame = 2500 #録画のフレーム数
    rec_flag = 0  #録画のフラグ
    i = 0 #カウンタ
    
    menu()

    while True:
        #フレーム読み込み
        ret, img = cap.read()
        height = img.shape[0]
        width = img.shape[1]
        converted_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


        #録画処理
        if i < max_frame and rec_flag == 1:
            rec.append(converted_img)
            i += 1


        #フレーム表示
        img = cv2.flip(img, 1)
        cv2.imshow('original', img) #自分でチェックするための出力
        sendframe(converted_img) #仮想カメラに出力
        

        #キー入力に応じて機能を選択
        key = cv2.waitKey(2)
        if key == 27:#escキーを押すと終了
            break

        elif key == 13: #エンターキーを押すと、録画開始　もう一度押すと停止(max約75sec)
            if rec_flag == 0:
                rec_flag = 1
                print("rec start")
            else: 
                rec_flag = 0
                print("rec stop")
                menu()

        elif key == 32: #スペースキーを押すと録画を再生
            rec_flag = 0
            play(rec)

        elif key == 9: #Tabキーを押すとフリーズ
            print("freeze")
            while cv2.waitKey(2) != 9:
                show_original()
            menu()

    #終了処理
    end_flag = 1
    cap.release()
    cv2.destroyAllWindows()
    print("<thread1 done>")


if __name__ == "__main__":
    main()
