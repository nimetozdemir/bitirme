import cv2
from functools import wraps 
from app import app
from flask import flash, request, redirect, url_for,render_template, session,Response
import mysql.connector
from functools import wraps
import pandas as pd
import os
import datetime


def conn():
    mydb = mysql.connector.connect(
        host="hypegenai.com",
        user="hypegena",
        password="aZ5xjXf133",
        database="hypegena_akilli_yoklama"
    )
    return mydb
app.secret_key = 'super secret'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args,**kwargs)
        else:
            return redirect(url_for("login"))
    return decorated_function


file = []

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    dersler=[]
    # form2=İndexForm2(request.form)
    file_on_url=""
    database_url=""
    mydb=conn()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM dersler")
    myresult = mycursor.fetchall()
    for x in myresult:
        dersler.append(x[1])
    if request.method == 'POST':
        isim_soyisim = request.form.get('isim_soyisim')
        okul_no = request.form.get('okul_no')
        ders = request.form.get('saat_start')
        file_on = request.files['file_on']
        if file_on and allowed_file(file_on.filename):
            file_on.save("./app/static/ogrenciler/"+str(okul_no)+"_1.jpg")
            file_on_url = "./app/static/ogrenciler/"+str(okul_no)+"_1.jpg"
            database_url='/static/database_id/'+str(okul_no)+'.png'

            file_on=cv2.imread(str(file_on_url))
            cv2.imwrite('./app/static/database_id/'+str(okul_no)+'.png', file_on)
        print(isim_soyisim,okul_no,ders)
                
        mycursor = mydb.cursor(buffered=True)
        all_kisiler='all_kisiler'
        mycursor.execute("insert into "+ders+"(school_no,name_surname,image)values(%s,%s,%s)",
                        (okul_no, isim_soyisim, database_url))
        mydb.commit()
        mycursor.execute("insert into "+all_kisiler+"(isim_soyisim,image)values(%s,%s)",
                        (isim_soyisim, database_url))
        mydb.commit()
        mycursor.close()
        
    return render_template("index.html",dersler=dersler)
    
okul=1
@app.route("/kisieklecanli", methods=['GET', 'POST'])
@login_required
def kisieklecanli():
    global okul
    if request.method == 'POST':
        okul+=1
        isim_soyisim = request.form.get('isim_soyisim')

        file_on = request.files['file_on']

        
        if file_on and allowed_file(file_on.filename):
            file_on.save("./app/static/ogrenciler/"+str(okul)+"_1.jpg")
            file_on_url = "./app/static/ogrenciler/"+str(okul)+"_1.jpg"
            database_url='/static/database_id/'+str(okul)+'.png'

            file_on=cv2.imread(str(file_on_url))
            cv2.imwrite('./app/static/database_id/'+str(okul)+'.png', file_on)
        # print(isim_soyisim,okul_no,ders)
        mydb=conn()        
        mycursor = mydb.cursor(buffered=True)
        ders='all_kisiler'
        mycursor.execute("insert into "+ders+"(isim_soyisim,image)values(%s,%s)",
                        (isim_soyisim, database_url))
        mydb.commit()
        mycursor.close()
        
    return render_template("kisieklecanli.html")
    



@app.route("/yoklamalistesicanli", methods=['GET', 'POST'])
@login_required
def yoklamalistesicanli():
    
    dersler=[]
    mydb=conn()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM dersler")
    myresult = mycursor.fetchall()
    for x in myresult:
        dersler.append(x[1])
    if request.method == 'POST':
        date=request.form.get("date1")
        ders=request.form.get("ders")
        print(date,ders)

        bas = pd.read_csv("./app/static/"+str(date)+"/kisiler.csv",index_col=0)
        print(bas)
        # bas.rename({"name": "name_surname", "okul_no": "okul_no","ders": "ders","time": "time"}, axis='columns', inplace =True)
        # bas.drop('Unnamed: 0', axis=1, inplace=True)
        # bas.drop('Unnamed: 0', axis=1, inplace=True)
        print(bas)
        name=bas['name']
        okul_numarasi=bas['okul_numarasi']
        ders_adi=bas['ders_adi']
        time=bas['time']
        return render_template("yoklamalistesicanli.html",dersler=dersler,bas=bas,name=name,okul_numarasi=okul_numarasi,ders_adi=ders_adi,time=time) 

    # data = pd.read_csv(mkdir_folder_str)
    return render_template("yoklamalistesicanli.html",dersler=dersler) 




def gen_frames():  
    camera=cv2.VideoCapture('nimet.mp4')
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route("/video_feed", methods=['GET', 'POST'])
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/canli", methods=['GET', 'POST'])
def canli():
    return render_template('canli.html') 





@app.route("/dersekle", methods=['GET', 'POST'])
@login_required
def dersekle():
    if request.method == 'POST':
        saat_start=request.form.get('saat_start')
        saat_stop=request.form.get('saat_finish')
        gun=request.form.get('gun')
        ders_adi=request.form.get('ders_adi')
        mydb=conn()
        mycursor = mydb.cursor(buffered=True)

        
        # mycursor.execute(''' CREATE TABLE '''+ders_adi+''' (id int primary key,school_no varchar(255),name_surname varchar(255),image varchar(255)''')
        try:
            mycursor.execute("CREATE TABLE "+ders_adi.replace(" ","")+" (id INT AUTO_INCREMENT PRIMARY KEY, school_no VARCHAR(255), name_surname VARCHAR(255),image VARCHAR(255))")           
            # mydb.commit()ay
            flash("Kayit Başarılı","success")
        except:
            flash("Kayit Başarılı","danger")

        try:
            mycursor.execute("insert into dersler(dersadi,dersgirissaati,dersbitissaati,gun)values(%s,%s,%s,%s)",
                            (ders_adi, saat_start, saat_stop, gun))
            mydb.commit()
            mycursor.close()
            print(saat_start,saat_stop,gun,ders_adi)
            flash("Kayit Başarılı","success")
        except:
            flash("Kayit Başarılı","danger")
    return render_template("dersekle.html")


@app.route("/yoklamalistesi", methods=['GET', 'POST'])
@login_required
def yoklama():
    
    dersler=[]
    mydb=conn()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM dersler")
    myresult = mycursor.fetchall()
    for x in myresult:
        dersler.append(x[1])
    if request.method == 'POST':
        date=request.form.get("date1")
        ders=request.form.get("ders")
        print(date,ders)
        bas = pd.read_csv("./app/static/"+str(date)+"/"+str(ders)+".csv",index_col=0)
        print(bas)
        # bas.rename({"name": "name_surname", "okul_no": "okul_no","ders": "ders","time": "time"}, axis='columns', inplace =True)
        # bas.drop('Unnamed: 0', axis=1, inplace=True)
        # bas.drop('Unnamed: 0', axis=1, inplace=True)
        print(bas)
        name=bas['name']
        okul_numarasi=bas['okul_numarasi']
        ders_adi=bas['ders_adi']
        time=bas['time']
        return render_template("yoklamalistesi.html",dersler=dersler,bas=bas,name=name,okul_numarasi=okul_numarasi,ders_adi=ders_adi,time=time) 

    # data = pd.read_csv(mkdir_folder_str)
    return render_template("yoklamalistesi.html",dersler=dersler) 


@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


app.secret_key='super secret key'
@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("pass")
        mydb=conn()
        mycursor = mydb.cursor() 
        mycursor.execute("select*from user1 where mail='" +
                         email+"' and password='"+password+"'")
        myresult = mycursor.fetchall()
        if myresult:
            for i in myresult:
                print(i)
                session["username"]=i[1]
                session["yetki"]=i[4]
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



dizi=[[0,0,0,0]]
ogrenciler=pd.DataFrame(dizi,columns=['id','time','name','ders_adi'])
@app.route('/api/file', methods=['POST'])
def program_start():
    global ogrenciler
    mkdir_folder=str(datetime.datetime.now())
    mkdir_folder_str=(mkdir_folder[:10]).strip()
    try:
        path_bas="./app/static/"+str(mkdir_folder_str)
        os.mkdir(path_bas)
    except Exception as e:
        print(e)
    json = request.form.to_dict()
    # print(json)
    
    ogrenciler=ogrenciler.append(json,ignore_index=True)
    ogrenciler=ogrenciler.drop_duplicates(subset=['name'])
    print(ogrenciler)
    ogrenciler.to_csv(path_bas+"/"+str(json['ders_adi'])+".csv")
    return 'True'