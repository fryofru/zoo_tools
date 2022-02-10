# -*- coding: utf-8 -*-
#実行前に　sudo modprobe v4l2loopback devices=1

import cv2
import serial
import numpy as np
import threading
import pyfakewebcam

def main():
    
    #並列計算
    thread1 = threading.Thread(target = img_processing) #画像処理
    thread2 = threading.Thread(target = sensor) #センサー
    
    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("program all finished")


def menu():
    print("------------------------------------How to use------------------------------------")
    print("enter: rec/rec stop       space: play/play stop     Tab: freeze      escape: exit")
    line()

def line():
    print("---------------------------------------------------------------------------------")

def show_original():
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    cv2.imshow('original', img)

#録画した映像を再生
def play(rec, camera):
    print("playing...")
    j = 0
    t_freeze = 1000

    cv2.waitKey(t_freeze) #録画への切り替えのフリーズ1s（通信不良を装う）
    while cv2.waitKey(30) != 32: #エンターキーを押すと再生終了
        #cv2.imshow("video", rec[j])
        camera.schedule_frame(rec[j]) #仮想カメラに出力
        j += 1
        if j == len(rec):
            j = 0
        
        show_original()


    cv2.waitKey(t_freeze)#録画からの切り替えのフリーズ1s（通信不良を装う）

    print("stop playing")
    menu()


def img_processing():
    print("camera start")
    global cap
    cap = cv2.VideoCapture(1) #カメラから画像を読み込み
    camera = pyfakewebcam.FakeWebcam('/dev/video2', 640,480) #出力先の仮想カメラの設定
    rec = [] #動画の一時保存先
    
    global end_flag #sensor()を終わらせるフラグ スレッド間で共有
    end_flag =0 
    max_frame = 2500 #録画のフレーム数
    rec_flag = 0  #録画フラグ
    i = 0 #カウンタ
    notPresent = cv2.imread("riseki.png") #離席中の画像

    menu()

    while True:
        #離席中か判定
        while absent_flag == 2:
            frame = cv2.cvtColor(notPresent, cv2.COLOR_BGR2RGB) #BGRからRGBに変換
            frame = cv2.flip(frame,1) #画像を反転
            camera.schedule_frame(frame) #仮想カメラに出力
            cv2.waitKey(2)


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
        camera.schedule_frame(converted_img) #仮想カメラに出力
        

        #キー入力に応じて機能を選択
        key = cv2.waitKey(2)
        if key == 27:#escキーを押すと終了
            break

        elif key == 10: #エンターキーを押すと、録画開始　もう一度押すと停止(max約75sec)
            if rec_flag == 0:
                rec_flag = 1
                print("rec start")
            else: 
                rec_flag = 0
                print("rec stop")
                menu()

        elif key == 32: #スペースキーを押すと録画を再生
            rec_flag = 0
            play(rec, camera)

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

def sensor():
    print("sensor start")
    global absent_flag #2で離席中 スレッド間で共有
    absent_flag = 0

    ser = serial.Serial(port = '/dev/ttyUSB0', baudrate = 9600) #シリアル通信のための初期化
    
    while ser.is_open:
        x = ser.readline() #センサからの値を受け取る
        
        #センサの値が200(cm)より大きければ離席中と判定する
        if float(x) > 200:
            if absent_flag == 0:
                absent_flag = 1
            else: absent_flag = 2
                
        else:
            absent_flag = 0
        
        #終了判定
        if end_flag == 1:
            break

    ser.close
    print("<thread2 done>")


if __name__ == "__main__":
    main()
