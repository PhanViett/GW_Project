import re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_jwt_extended import JWTManager, create_access_token
from numpy.core.fromnumeric import var
from pymongo import MongoClient
from datetime import *

import numpy as np

import base64

# MONGO DATABASE CONNECTION
# Localhost
client = MongoClient("mongodb://localhost:27017/")
# Database Name
db = client["project"]
# Collection Name
demo = db["demo"]

user = db["user"]


app = Flask(__name__)
jwt = JWTManager(app)

# JWT Config
app.config["JWT_SECRET_KEY"] = "this-is-secret-key"

app.secret_key = "thiss-is-secret-key"
 
@app.route('/', methods=['GET','POST'], endpoint="prcimg")
def process_image():

    # inputImage is the name attribute of the <input> tag in the html
    inImg = request.files["inputImage"].

    encoded = base64.b64encode(inImg)
    mime = "image/jpg"
    mime = mime + ";" if mime else ";"
    input_image = "data:%sbase64,%s" % (mime, encoded)        

    return render_template("demo.html", {{ "inputImage": input_image }})


if __name__ == '__main__':
    app.run(debug=True)