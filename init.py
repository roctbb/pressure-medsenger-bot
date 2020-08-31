import datetime
import time
from threading import Thread
from flask import Flask, request, render_template, flash, redirect, url_for
import json
import requests
from config import *
from const import *
from flask_sqlalchemy import SQLAlchemy
from multiprocessing import Process
from classes.colorok import *
from classes.aux import *
from classes.db import *

out_green_light('SCRIPT STARTED')
app = Flask(__name__)
# app.config.from_object(__name__)
db_uri = "postgres://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config.update(ENV='developer')
# app.config.update(DEBUG=True)
app.config.update(SECRET_KEY='JKJH!Jhjhjhj456545_jgnbh~hfgbgb')
db = SQLAlchemy(app)