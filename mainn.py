from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_jwt_extended import JWTManager, create_access_token
from pymongo import MongoClient
from datetime import *

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


asp=[]
asp.append("1")
asp.append("2")
asp.append("3")
asp.append("4")
asp.append("5")
asp.append("6")
asp.append("7")
asp.append("8")
asp.append("9")

for x in asp:
    print(x)