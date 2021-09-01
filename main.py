import re

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from pymongo import MongoClient
from flask_pymongo import PyMongo
import numpy as np
import pickle
from datetime import *

app = Flask(__name__)

# MONGO DATABASE CONNECTION
# Localhost
client = MongoClient("mongodb://cluster-shard-00-01.2hp1c.mongodb.net:27017/")
# Database Name
db = client["HPA-SYSTEM"]
# Collection Name
user = db["users"]
# Collection Name
news = db["news"]

app.config['MONGO_URI'] = 'mongodb://cluster-shard-00-01.2hp1c.mongodb.net:27017/HPA-SYSTEM'

jwt = JWTManager(app)

mongo = PyMongo(app)

# JWT Config
app.config["JWT_SECRET_KEY"] = "this-is-secret-key"

app.secret_key = "thiss-is-secret-key"

model = pickle.load(open('model.pkl', 'rb'))

app.jinja_env.globals.update(zip=zip)

AVATAR_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@app.route('/')
def default():
    if 'member' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

def avatar_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in AVATAR_ALLOWED_EXTENSIONS

def validation(variable_list, *args):
    i = 0
    index = []
    validate = []
    cln = []
    cld = []
    nokidx = []
    nokvalues = []
    msg = []


    for value in args:
        if not re.search("^[a-zA-Z0-9\s]*$", value): 
            i += 1
            validate.append("n-ok")
            index.append(i)
        else: 
            i += 1
            validate.append("ok")
            index.append(i)        
        if not re.search("^.{4,}$", value):
            i += 1
            validate.append("n-ok")
            index.append(i)
        else: 
            i += 1
            validate.append("ok") 
            index.append(i)
        if not re.search("^.{1,50}$", value):
            i += 1
            validate.append("n-ok")
            index.append(i)
        else: 
            i += 1
            validate.append("ok")
            index.append(i)

            arr_err = validate
            arr_idx = index

    for x,y in zip(arr_err, arr_idx):
        if x == "n-ok":
            nokvalues.append("arr_err[" + str(y) + "]")
            nokidx.append(y)

    for z in nokidx:
        cln.append(z//3)    
        cld.append(z%3)

    for a,b in zip(cld,cln):
        if a == 1:
            msg.append(str(variable_list[b]) + " cannot contain special characters")
        elif a == 2:
            msg.append(str(variable_list[b]) + " has lower limit characters equal 4")  
        elif a == 0:
            msg.append(str(variable_list[b-1]) + " has upper limit characters equal 50")  
    
    return msg


# Register.html
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        i = 0
        err_name = []
        err_username  = []
        err_password = []

        username = request.form["username"]
        name = request.form["name"]
        password = request.form["password"]
        email = request.form["email"]
        user_i4 = user.find_one({"username": username})

        variable_list = ["Name","Username","Password"]

        err_msg = validation(variable_list, username, name, password)


        for x in err_msg:
            i += 1
            x_split = x.split()
            if x_split[0] == "Name":
                err_name.append(err_msg[i-1])
            if x_split[0] == "Username":
                err_username.append(err_msg[i-1])
            elif x_split[0] == "Password":
                err_password.append(err_msg[i-1])

        # User Create Process
        if len(err_msg) == 0:
            if user_i4:
                flash("User Already Exist !!!", "warning")
                return redirect(request.url)
            else:
                user_count = len(list(user.find()))
                if user_count == 0:
                    count = 1
                else:
                    count = len(list(user.find())) + 1 

                # User Statics
                dob = '1997-01-01'
                height = 1
                weight = 1
                gender = 1
                chol = 1
                gluc = 1
                smoke = 0
                alco = 0
                active = 0
                role = ["user"]
                avatar="file/avatar.jpg"
                # records = {}
                user_info = dict(name=name, username=username, password=password, email=email, avatar=avatar,
                                dob=dob, height=height, weight=weight, role=role, count=count,
                                chol=chol, gender=gender, smoke=smoke, alco=alco, active=active, gluc=gluc)
                user.insert_one(user_info)
                flash("User is created successfully !!!", "success")
            return redirect(url_for('register'))
        else:
            return render_template("register.html", err_name=err_name, err_username=err_username, err_password=err_password)

    return render_template('register.html')

# Register.html
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form["username"]
        password = request.form["password"]

        err = []
        err_username = []

        if not re.search("^[a-zA-Z0-9\s]*$", username):
            err_username.append("Username should only contain alphanumeric characters")
            return render_template("login.html", err_username=err_username)
        else: 
            user_i4 = user.find_one({"username": username, "password": password})
            if user_i4:
                access_token = create_access_token(identity=username)
                session['member'] = True
                session['id'] = str(user_i4['_id'])
                session['accesstoken'] = access_token
                session['username'] = user_i4['username']
                session['name'] = user_i4['name']
                session['role'] = user_i4['role']
                # Saved another statics of user into session
                session['dob'] = user_i4['dob']
                session['gender'] = user_i4['gender']
                session['height'] = user_i4['height']
                session['weight'] = user_i4['weight']
                session['ap_hi'] = user_i4['ap_hi']
                session['ap_lo'] = user_i4['ap_lo']
                session['chol'] = user_i4['chol']
                session['gluc'] = user_i4['gluc']
                session['smoke'] = user_i4['smoke']
                session['alco'] = user_i4['alco']
                session['active'] = user_i4['active']
                return redirect(url_for('index'))
            else:
                err.append("Username or Password is Incorrect")
            return render_template("login.html", err=err)
    else:
        print("Username and Password cannot be blank")
    return render_template('login.html')

# Index
@app.route("/index", methods=['GET','POST'])
def index():
    if 'member' in session:
        user_i4_username = session['username']
        user_i4 = user.find_one({"username": user_i4_username})

        data_news = news.find()
        list_news = list(data_news)

        time_diff=[]

        for x in list_news:
            space = datetime.now() - x["submitDate"]
            change = str(space).split(",")
            print("In CHANGE")
            print(change)
            if len(change) > 1: 
                print("Chay IF tren")
                time_diff.append(str(change[0]) + ' ago')
                print(change[0])
            else:
                if change[0] == 0: 
                    print("Chay IF")
                    time_diff.append(change[1] + ' minutes ago')
                elif int(change[0]) > 0 and int(change[0] < 24): 
                    print("Chay ELIF")
                    time_diff.append(change[0] + ' hours ago ')
        return render_template("index.html", user_i4=user_i4, newss=list_news, spaces=time_diff)
    else:
        return render_template("login.html")

# Profile
@app.route('/profile', methods=['GET'])
def profile():
    if 'member' in session:
        user_i4_username = session['username']
        user_i4 = user.find_one({"username": user_i4_username})
        return render_template('profile.html', user_i4=user_i4)

@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        user_i4_username = session['username']
        user_i4_filter = {'username': session['username']}
        user_i4 = user.find_one({"username": user_i4_username})

        name = request.form["name"]
        form_height = request.form["height"]
        form_weight = request.form["weight"]

        err_height = []
        err_weight = []
        variable_list = ["Name"]

        err_msg = validation(variable_list, name)

        if not re.search("^[0-9]*$", form_height):
            err_height.append("Height value just only contain number")
        else: 
            height = "OK" 
 
        if not re.search("^[0-9]*$", form_weight):
            err_weight.append("Weight value just only contain number")
        else: 
            weight = "OK"   

        if len(err_msg) == 0 and height == "OK" and weight == 'OK':
            user_i4_update = {"$set": {'name': request.form['name'],
                                       'avatar': str("file/" + str(request.files['avatar'].filename)),
                                       'dob': request.form['dob'],
                                       'gender': int(request.form['gender']),
                                       'height': request.form['height'],
                                       'weight': request.form['weight'],
                                       'chol': int(request.form['chol']),
                                       'gluc': int(request.form['gluc']),
                                       'smoke': int(request.form['smoke']),
                                       'alco': int(request.form['alco']),
                                       'active': int(request.form['active'])}}
            user.update_one(user_i4_filter, user_i4_update)
            user_i4 = user.find_one({"username": user_i4_username})
            return render_template('profile.html', user_i4=user_i4)
        else:
            return render_template('profile.html', user_i4=user_i4, err_msg=err_msg, err_height=err_height, err_weight=err_weight)         

# Measure
@app.route('/measure')
def measure():
    if 'member' in session:
        user_i4_username = session['username']
        user_i4 = user.find_one({"username": user_i4_username})
        return render_template('measure.html', user_i4=user_i4)

@app.route('/predict', methods=["POST"])
def predict():
    if 'member' in session:
        user_i4_filter = {'username': session['username']}


        if request.method == 'POST' and "ap_hi" in request.form and "ap_lo" in request.form:

            date_date = date.today()

            current_date = str(date_date.day) + '/' + str(date_date.month) + '/' + str(date_date.year)

            current_year = date_date.year
            dob_str = session['dob']
            splited = dob_str.split("-")
            prd_age_int = splited[0]
            age_day = int(current_year) - int(prd_age_int)

            # age_year = int(current_year) - int(prd_age_int)
            # leap_year = math.floor(age_year / 4) 
            # age_day = (age_year * 365) + leap_year
            
            prd_age = age_day

            prd_gender = session['gender']
            prd_height = session['height']
            prd_weight = session['weight']
            prd_ap_hi = request.form['ap_hi']
            prd_ap_lo = request.form['ap_lo']
            # request.form['ap_hi'] = session['height']
            # request.form['ap_lo'] = session['height']
            prd_chol = session['chol']
            prd_gluc = session['gluc']
            prd_smoke = session['smoke']
            prd_alco = session['alco']
            prd_active = session['active']

            # Array Generator
            list_parameters = []
            list_parameters.append(prd_age)
            list_parameters.append(prd_gender)
            list_parameters.append(prd_height)
            list_parameters.append(prd_weight)
            list_parameters.append(prd_ap_hi)
            list_parameters.append(prd_ap_lo)
            list_parameters.append(prd_chol)
            list_parameters.append(prd_gluc)
            list_parameters.append(prd_smoke)
            list_parameters.append(prd_alco)
            list_parameters.append(prd_active)
            array_features = [np.array(list_parameters)]
            prediction = model.predict(array_features)

            output = int(prediction)

            # Object Generator
            obj_parameters = { 'age': str(prd_age),
                               'date': str(current_date),
                               'gender': str(prd_gender),
                               'height': str(prd_height),
                               'weight': str(prd_weight),
                               'ap_hi': str(prd_ap_hi),
                               'ap_lo': str(prd_ap_lo),
                               'chol': str(prd_chol),
                               'gluc': str(prd_gluc),
                               'smoke': str(prd_smoke), 
                               'alco': str(prd_alco),
                               'active': str(prd_active),
                               'cardio': str(output)
                             }

            user.update_one(user_i4_filter,{'$push': {'records': obj_parameters}})

            if output == 1:
                return render_template('measure.html',
                                    result='BAN KHONG CO NGUY CO BI BENH TIM!NHO GIU GIN SUC KHOE BAN NHE ')
            else:
                return render_template('measure.html',
                                    result='BAN SE BI BENH TIM DAY! NEN TAP THE DUC DEU DAN DI NHA')

# Records
@app.route('/records')
def records():
    if 'member' in session:
        user_i4_username = session['username']
        user_i4 = user.find_one({"username": user_i4_username})
        user_i4_filter = {'username': session['username']}

        dict_records = user.find_one(user_i4_filter, {"records":True, "_id":False})
        for list_records in dict_records.values():
            print(list_records)
            print(len(list_records))
            return render_template('records.html', user_i4=user_i4, datas=list_records)
    else:
        jsonify("liliu")
    return render_template('records.html')

# Tips
@app.route('/news')
def newlist():
    if 'member' in session:
        user_i4_username = session['username']
        user_i4 = user.find_one({"username": user_i4_username})

        data_news = news.find()
        list_news = list(data_news)

        time_diff=[]

        for x in list_news:
            space = datetime.now() - x["submitDate"]
            change = str(space).split(",")
            print("In CHANGE")
            print(change)
            if len(change) > 1: 
                print("Chay IF tren")
                time_diff.append(str(change[0]) + ' ago')
                print(change[0])
            else:
                if change[0] == 0: 
                    print("Chay IF")
                    time_diff.append(change[1] + ' minutes ago')
                elif int(change[0]) > 0 and int(change[0] < 24): 
                    print("Chay ELIF")
                    time_diff.append(change[0] + ' hours ago ')

        return render_template("news.html", user_i4=user_i4, newss=list_news, spaces=time_diff)
    else:
        return render_template("login.html")

# Manage Users
@app.route('/manage/users', endpoint='manageusers')
def manageusers():
    for user_role in session['role']:
        if 'member' in session and user_role == 'admin':
            user_i4_username = session['username']
            user_i4 = user.find_one({"username": user_i4_username})
            
            data_user = user.find()
            list_users = list(data_user)                
            return render_template('ad_users.html', user_i4=user_i4, datas=list_users)
        else:
            print("You do not have enough permission to access this resouce")
    return render_template('ad_users.html')

@app.route('/manage/users/create', methods=['POST'], endpoint='admincreate')
def admincreate():
    for user_role in session['role']:
        if 'member' in session and user_role == 'admin':
            user_i4_username = session['username']
            user_i4 = user.find_one({"username":user_i4_username})

            i = 0
            err_name = []
            err_exist = []
            err_password = []
            err_username  = []

            name = request.form["name"]
            email = request.form["email"]
            username = request.form["username"]
            password = request.form["password"]

            variable_list = ["Name","Username","Password"]
            err_msg = validation(variable_list, username, name, password)

            user_i4_new = user.find_one({"username": request.form['username']})

            
            for x in err_msg:
                i += 1
                x_split = x.split()
                if x_split[0] == "Name":
                    err_name.append(err_msg[i-1])
                if x_split[0] == "Username":
                    err_username.append(err_msg[i-1])
                elif x_split[0] == "Password":
                    err_password.append(err_msg[i-1])

            # User Create Process
            if len(err_msg) == 0:
                if user_i4_new:
                    return err_exist.append("User Already Exist !!!")
                else:
                    user_count = len(list(user.find()))
                    if user_count == 0:
                        count = 1
                    else:
                        count = len(list(user.find())) + 1 

                    # User Statics
                    dob = '1997-01-01'
                    height = 1
                    weight = 1
                    gender = 1
                    chol = 1
                    gluc = 1
                    smoke = 0
                    alco = 0
                    active = 0
                    role = ["user"]
                    avatar="file/avatar.jpg"
                    # records = {}
                    user_info = dict(name=name, username=username, password=password, email=email, avatar=avatar,
                                    dob=dob, height=height, weight=weight, role=role, count=count,
                                    chol=chol, gender=gender, smoke=smoke, alco=alco, active=active, gluc=gluc)
                    user.insert_one(user_info)
                    flash("User is created successfully !!!", "success")
                return render_template("ad_users.html", user_i4=user_i4, err_name=err_name, err_username=err_password, err_exist=err_exist)
            else:
                return print("Bạn không đủ quyền hạn để truy cập vùng này, sẽ có cập nhật trang web trong tương lai")
        return redirect(url_for(manageusers))

@app.route('/manage/users/update', methods=['GET', 'POST'])
def adminupdate(): 
    
    if request.method == 'POST':
        user_i4_count = int(request.form['count'])
        user_i4_filter = {'count': user_i4_count}
        user_i4 = user.find_one({"count": user_i4_count})
        print(user_i4)

        name = request.form["name"]
        email = request.form["email"]
        height = request.form["height"]
        weight = request.form["weight"]

        # Name Validation
        if not re.search("^[a-zA-Z0-9\s]*$", name):
            name_1 = "n-OK"
            flash("Name should only contain alphanumeric characters","warning")
        else: 
            name_1 = "OK"        
        if not re.search("^.{4,}$", name):
            name_2 = "n-OK"
            flash("Name should has at least 4 characters","warning")
        else: 
            name_2 = "OK"      
        if not re.search("^.{1,50}$", name):
            name_3 = "n-OK"
            flash("Name should not has over 50 characters","warning")
        else: 
            name_3 = "OK"
        if name_1 == "OK" and name_2 == "OK" and name_3 == "OK": 
            form_name = "OK" 
        else: 
            form_name = "n-OK"

        # Height Validation
        if not re.search("^[0-9]*$", height):
            form_height = "n-OK"
            flash("Height should only contain numeric characters", "height")
        else: 
            form_height = "OK" 
 
        # Weight Validation
        if not re.search("^[0-9]*$", weight):
            form_weight = "n-OK"
            flash("Name should only contain numeric characters","weight")
        else: 
            form_weight = "OK"   
        
        # Email Validation
        email_pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
        if not re.match(email_pattern, email):
            flash("Invalid Email","warning")
            form_email = "n-OK"
        else:
            form_email = "OK"

        if form_name == "OK" and form_height == "OK" and form_weight == "OK" and form_email == "OK":
            list_array = []
            list_array.append(request.form['role'])
            user_i4_update = {"$set": {'name': request.form['name'],
                                       'role': list_array,
                                       'dob': request.form['dob'],
                                       'email': request.form['email'],
                                       'gender': int(request.form['gender']),
                                       'height': request.form['height'],
                                       'weight': request.form['weight'],
                                       'chol': int(request.form['chol']),
                                       'gluc': int(request.form['gluc']),
                                       'smoke': int(request.form['smoke']),
                                       'alco': int(request.form['alco']),
                                       'active': int(request.form['active'])}}
            print(user_i4_update)
            user.update_one(user_i4_filter, user_i4_update)
            userxx = user.find_one(user_i4_filter)
            print(userxx)
            data_user = user.find()
            list_users = list(data_user)   
            redirect(url_for('manageusers', datas=list_users))
            return redirect(url_for('manageusers'))
        return render_template('ad_users.html')

@app.route('/manage/users', methods=['POST'], endpoint='userdelete')
def admindelete():
    user_i4_count = int(request.form['count'])
    user_i4_filter = {"count": user_i4_count}
    user.delete_one(user_i4_filter)

    data_user = user.find()
    list_users = list(data_user)  
    redirect(url_for('manageusers', datas=list_users))
    return redirect(url_for('manageusers'))

# Manage News
@app.route('/manage/news', methods=['GET', 'POST'], endpoint='managenews')
def managenews(): 
    for user_role in session['role']:
        if 'member' in session and user_role == 'admin':
            user_i4_username = session['username']
            user_i4 = user.find_one({"username": user_i4_username})
            
            imgfile = []

            news_i4 = news.find()
            list_news_i4 = list(news_i4)
            for x in list_news_i4: 
                # x_split = x["file"].split("/")[1]
                imgfile.append(x["file"].split("/")[1])
                print(imgfile)
                for y, z in zip(imgfile, list_news_i4):
                    z["file"] = y
                    # print(type(y["file"]))
                    print(" ")
                    print("In Y")
                    print(y)
                    print(type(y))
                    print(" ")
                    print("In Z")
                    print(z)
                    print(type(z))

            return render_template("ad_news.html", user_i4=user_i4, newss=list_news_i4)
        else:
            print("You do not have enough permission to access this resouce")
    return render_template("ad_news.html")

@app.route('/manage/news', methods=['POST'], endpoint='newdelete')
def admindelete():
    user_i4_count = int(request.form['count'])
    user_i4_filter = {"count": user_i4_count}
    user.delete_one(user_i4_filter)

    data_user = user.find()
    list_users = list(data_user)  
    redirect(url_for('manageusers', datas=list_users))
    return redirect(url_for('manageusers'))

@app.route('/manage/news/upload', methods=['POST'], endpoint='upload')
def newsupload():
    if request.method == 'POST':

        news_count = len(list(news.find()))
        if news_count == 0:
            news_count = 1
        else:
            news_count = len(list(news.find())) + 1 

        current_date = datetime.today()
        current_day = str(current_date.day) + '-' + str(current_date.month) + '-' + str(current_date.year)
        current_time = str(current_date.hour) + ':' + str(current_date.minute) + ':' + str(current_date.second)

        form_file_title = request.form['title']
        form_file = request.files['news_image']
        mongo.save_file(form_file.filename, form_file)

        news.insert_one({"count": news_count,
                         "title": form_file_title, 
                         "file": "file/" + str(form_file.filename),
                         "author": str(request.form['author']),
                         "link": str(request.form['link']),
                         "submitDate": datetime.now(),
                         "submitTime": current_time,
                         "submitDay": current_day })

    return redirect(url_for("managenews"))

# File Upload
@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

# Logout
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('password', None)
    session.pop('role', None)
    session.pop('dob', None)
    session.pop('height', None)
    session.pop('weight', None)
    session.pop('gender', None)
    session.pop('ap_hi', None)
    session.pop('ap_lo', None)
    session.pop('chol', None)
    session.pop('gluc', None)
    session.pop('smoke', None)
    session.pop('alco', None)
    session.pop('active', None)
    session.pop('cardio', None)

    # Redirect to login page
    return redirect(url_for('login'))

# Demo for test
@app.route('/demo')
def demo():
    return render_template("demo.html")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)



