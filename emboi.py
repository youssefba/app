from flask_appconfig import AppConfig
from flask import Flask, render_template, request, Response, redirect, url_for
from flask_bootstrap import Bootstrap

from datetime import datetime
import time
import os
import subprocess
from functools import wraps
import numpy
import random
import json
from flask import send_from_directory
from werkzeug import secure_filename

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = set(['xls','xlsx'])
MAX_PASSENGERS = 19

auth = {"user":"emboi","password":"emboi"}

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == auth["user"] and password == auth["password"]

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

class xlsManagement(object):
    def __init__(self,entryData=None,dataKeys=None):
        self.entryData = entryData
        self.dataKeys = dataKeys

xls = xlsManagement()

def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    @app.route('/up')
    @requires_auth
    def showCounters():
		#return "Hello there, this will be a transport management app"
		return render_template('index.html')

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @app.route('/', methods=['GET', 'POST'])
    @requires_auth
    def upload_file():
        entryData = dataKeys = settings =  None
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #return redirect(url_for('uploaded_file',filename=filename))
                p = subprocess.Popen(['xlsx2csv', filename], stdout=subprocess.PIPE)
                out, err = p.communicate()
                xls.entryData,xls.dataKeys = getFormattedData(out)
        settings = loadSettings()
        return render_template('index.html',settings = settings,entryData = xls.entryData, dataKeys = xls.dataKeys)

    @app.route('/generate', methods=['GET', 'POST'])
    @requires_auth
    def download_file():
        settings = loadSettings()
        dataKeys = xls.dataKeys
        entryData = xls.entryData
        countList =  getCountList()


        return redirect(url_for('uploaded_file',filename="result.csv"))

    def loadSettings():
        """ zones in static order, will be dynamic in further versions """
        result = None
        with open("templates/settings.json","r") as settings:
            result =  settings.read()
        return [x.split(">") for x in result.split(",")]
        #return "a,b,f,i,n1,o,d,c,e,g,h,i,m,k,n2"

    def getCountList():
        entry = [ [y for y in xls.entryData if y["heure"] in x]  for x in set([z["heure"] for z in xls.entryData])]
        countList = []
        for subList in entry:
            subDicos = {}
            for item in subList:
                try:
                    subDicos[item["code"]] += int(item["nombre"])
                except:
                    subDicos[item["code"]] = int(item["nombre"])
            countList.append({"data":subDicos,"heure":item["heure"]})
        return countList


    def getFormattedData(dataIn):
        entryDataTmp = dataIn.split("\n")
        entryDataTmp = [x.split(",") for x in entryDataTmp]
        dataKeys = entryDataTmp[0]
        entryData = []
        for item in entryDataTmp[1:]:
            curTime = item[0] if item[0] else curTime
            newItem = {}
            newItem[dataKeys[0]] = curTime
            for key,value in zip(dataKeys[1:],item[1:]):
                newItem[key] = value
            entryData.append(newItem)
        return entryData[:-1],dataKeys


    @app.route('/uploads/<filename>')
    @requires_auth
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

    return app

if __name__ == '__main__':
    create_app().run(host="0.0.0.0",debug=True)
