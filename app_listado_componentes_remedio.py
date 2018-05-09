
from flask import Flask, redirect, url_for, request, render_template, jsonify
import sys
import os
import uuid
import urllib.request
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])

def inicio():
    data = None
    if request.method == 'POST':
        data = request.json
        try:
            #Aciclovir
            with open("https://www.laboratoriochile.cl/productos/?nombre-producto="+data['remedio']) as fp:
                soup = BeautifulSoup(fp)
            soup = soup.find("div", {"id": "productos-body"})
            soup = soup.find_all("p")
        except Exception as e:
            return e
    else:
        return 'nada que ver...'
if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True , port = 5001)