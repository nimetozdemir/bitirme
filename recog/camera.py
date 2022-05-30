from scipy.spatial.distance import cosine
import mtcnn
from keras.models import load_model
import pickle
import numpy as np
import cv2
from sklearn.preprocessing import Normalizer
import mysql.connector
import datetime
import os
import requests
import urllib.request
from datetime import datetime
import subprocess
import tensorflow as tf

rtmp_url = "rtmp://213.226.117.171:1935/hypegenai/CAM1"


mydb = mysql.connector.connect(
    host="hypegenai.com",
    user="hypegena",
    password="aZ5xjXf133",
    database="hypegena_akilli_yoklama"
)



def get_encode(face_encoder, face, size):
    face = normalize(face)
    face = cv2.resize(face, size)
    encode = face_encoder.predict(np.expand_dims(face, axis=0))[0]
    return encode
    
def get_face(img, box):
    x1, y1, width, height = box
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    face = img[y1:y2, x1:x2]
    return face, (x1, y1), (x2, y2)

l2_normalizer = Normalizer('l2')

def normalize(img):
    mean, std = img.mean(), img.std()
    return (img - mean) / std

def load_pickle(path):
    with open(path, 'rb') as f:
        encoding_dict = pickle.load(f)
    return encoding_dict

def recognize(img,detector,encoder,encoding_dict,sinif,ders,recognition_t=0.6,confidence_t=0.99,required_size=(160, 160), ):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = detector.detect_faces(img_rgb)
    for res in results:
        if res['confidence'] < confidence_t:
            continue
        face, pt_1, pt_2 = get_face(img_rgb, res['box'])
        encode = get_encode(encoder, face, required_size)
        encode = l2_normalizer.transform(encode.reshape(1, -1))[0]

        name = 'not recognize'
        distance = float("inf")
        for db_name, db_encode in encoding_dict.items():
            dist = cosine(db_encode, encode)
            if dist < recognition_t and dist < distance:
                name = db_name
                distance = float(1.0-dist)

        if name == 'not recognize':
            cv2.rectangle(img, pt_1, pt_2, (0, 0, 255), 2)
            cv2.putText(img, name, pt_1, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 1)
        else:
            # for c in sinif:
            #     print(name)
            #     if str(c) != str(name):
            #         name='not recognize'
            cv2.rectangle(img, pt_1, pt_2, (0, 255, 255), 2)
            cv2.putText(img, name + f'{distance:.2f}', (pt_1[0], pt_1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 200, 200), 2)
            mycursor = mydb.cursor()
            mycursor.execute("select school_no from "+ders+" where name_surname='"+name+"'")
            myresult = mycursor.fetchone()
            new_data={
                'time':str(datetime.now()),
                'name':name,
                'okul_numarasi':myresult,
                'ders_adi':ders
            }
            headers = {'Accept': 'application/json', }
            response = requests.post('http://localhost:5000/api/file', headers=headers,data=new_data)
            print(response.status_code)
    return img



def train(encoder_model,encodings_path,people_dir,l2_normalizer,face_detector,face_encoder):
    # global encoder_model , encodings_path ,people_dir,l2_normalizer,face_detector,face_encoder
    required_size = (160, 160)
    encoding_dict = dict()

    for person_name in os.listdir(people_dir):
        person_dir = os.path.join(people_dir, person_name)
        encodes = []
        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            img = cv2.imread(img_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 

            results = face_detector.detect_faces(img_rgb)
            if results:
                res = max(results, key=lambda b: b['box'][2] * b['box'][3])
                face, _, _ = get_face(img_rgb, res['box'])

                face = normalize(face)
                face = cv2.resize(face, required_size)
                encode = face_encoder.predict(np.expand_dims(face, axis=0))[0]
                encodes.append(encode)
        if encodes:
            encode = np.sum(encodes, axis=0)
            encode = l2_normalizer.transform(np.expand_dims(encode, axis=0))[0]
            encoding_dict[person_name] = encode
    
    for key in encoding_dict.keys():
        print(key)

    with open(encodings_path, 'bw') as file:
        pickle.dump(encoding_dict, file)
    
    return True

def conn():
    mydb = mysql.connector.connect(
        host="hypegenai.com",
        user="hypegena",
        password="aZ5xjXf133",
        database="hypegena_akilli_yoklama"
    )
    return mydb

sayac=0
people_count=[]
if __name__ == '__main__':
    encoder_model = 'data/model/facenet_keras.h5'
    encodings_path = 'data/encodings/encodings.pkl'
    # print(encoder_model)
    # print(os.listdir('data/model/facenet_keras.h5'))
    face_detector = mtcnn.MTCNN()
    face_encoder = load_model(encoder_model)
    encoding_dict = load_pickle(encodings_path)
    people_dir = './data/people'
    
    vc = cv2.VideoCapture(0)
    # fps = int(vc.get(cv2.CAP_PROP_FPS))
    # width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # command = ['./ffmpeg.exe',
    #        '-y',
    #        '-f', 'rawvideo',
    #        '-vcodec', 'rawvideo',
    #        '-pix_fmt', 'bgr24',
    #        '-s', "{}x{}".format(width, height),
    #        '-r', str(fps),
    #        '-i', '-',
    #        '-c:v', 'libx264', 
    #        '-pix_fmt', 'yuv420p',
    #        '-preset', 'ultrafast',
    #        '-f', 'flv',
    #        rtmp_url]

    # p = subprocess.Popen(command, stdin=subprocess.PIPE)
    
    while vc.isOpened():
        
        sinif=[]
        people=[]
        ret, frame = vc.read()
        if not ret:
            print("no frame:(")
            break
        mycursor=conn()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM dersler")
        myresult = mycursor.fetchall()
        stime=datetime.now()
        # stime=str(stime)[11:16]
        # stime=datetime.datetime.strptime(stime,'%H:%M').date()
        mycursor = mydb.cursor(buffered=True)
        for x in myresult:
            baslangic=datetime.strptime(x[2],'%H:%M') 
            bitis=datetime.strptime(x[3],'%H:%M')
            now = datetime.now()
            stime=str(now)[11:16]
            stime = now.strptime(str(stime),"%H:%M")
            print("time:", stime)
            print(bitis >= stime)
            print('---')
            print(stime >= baslangic)

            # if stime >= baslangic and bitis >= stime:    
            # if(stime)==x[2]:
            mycursor=conn()
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("SELECT * FROM "+str(x[1]))
            ogrenciler = mycursor.fetchall()
                            
            # if stime != x[3]:
            # print(json.dumps(sinif, ensure_ascii=False))
            # if stime != x[3]:
            # test=[]

            for ogrenci in ogrenciler:
                sinif.append(str(ogrenci['name_surname']).lower())
                
                for c in sinif:
                    # print(c)
                    if not c in people:
                        if len(c) > 1:
                            try:
                                path_bas=people_dir+"/"+str(c)
                                os.mkdir(path_bas)
                                imgURL = "http://localhost:5000/"+ogrenci['image']
                                urllib.request.urlretrieve(imgURL,people_dir+"/"+str(c)+"/"+"1.jpg")
                                sayac+=1
                            except Exception as e:
                                pass
                    
        print(sayac)
        if sayac==1:
            value=train(encoder_model,encodings_path,people_dir,l2_normalizer,face_detector,face_encoder)
            sayac=0
        # else:
        #     # frame = recognize(frame, face_detector, face_encoder, encoding_dict)
        #     print('a')
        # p.stdin.write(frame.tobytes())
        frame = recognize(frame, face_detector, face_encoder, encoding_dict,sinif,x[1])
                ########################################################################################################
                ####################################################################################################
        # frame = recognize(frame, face_detector, face_encoder, encoding_dict)
        
        
        
        # p.stdin.write(frame.tobytes())
        cv2.imshow('camera', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



