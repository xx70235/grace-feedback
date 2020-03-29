from flask import Flask
from app.config import Config as cfg
app = Flask(__name__, template_folder="templates")
# app.debug = True
app.secret_key = cfg.SECRET_KEY
from app import routes