
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
            url = urllib.request.urlopen("https://www.laboratoriochile.cl/productos/?nombre-producto="+data['remedio'])
            with url as fp:
                soup = BeautifulSoup(fp)
            soup = soup.find("div", {"id": "productos-body"})
            soup = soup.find_all("p")
            compuestos = None
            for datos in soup:
                datos      = datos.find("a").getText()
                if 'mg' in datos or '%' in datos:
                    compuestos = datos.split(" ")
                    compuestos = compuestos[0]
            return jsonify(
                    remedio   = data['remedio'],
                    compuesto = compuestos
                )
        except Exception as e:
            return jsonify(
                    error = e
                )
    else:
        return 'nada que ver...'
if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True , port = 5001)