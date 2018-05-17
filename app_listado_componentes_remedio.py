
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

#https://vsearch.nlm.nih.gov/vivisimo/cgi-bin/query-meta?v%3Aproject=medlineplus-spanish&v%3Asources=medlineplus-spanish-bundle&query=Galactosemia&_ga=2.158284350.541628268.1526482269-1655826678.1516816113

@app.route('/buscarterminomedico', methods = ['GET','POST'])

def buscarterminomedico():
    data = None
    if request.method == 'POST':
        data = request.json
        try:
            url = urllib.request.urlopen("https://vsearch.nlm.nih.gov/vivisimo/cgi-bin/query-meta?v%3Aproject=medlineplus-spanish&v%3Asources=medlineplus-spanish-bundle&query="+data['termino']+"&_ga=2.158284350.541628268.1526482269-1655826678.1516816113")
            with url as fp:
                soup = BeautifulSoup(fp)
            soup = soup.find("li", {"id": "doc-Ndoc1"})
            soup = soup.find("div", {"class": "document-footer"})
            soup = soup.find("span", {"class": "url"}).getText()
            url  = urllib.request.urlopen(soup)
            with url as fp:
                soup = BeautifulSoup(fp)
            queEs  = soup.find("div", {"id": "ency_summary"}).getText()
            causas = soup.find("div", {"class": "section-body"}).getText()
            print(queEs)
            print("-------------")
            print(causas)
            return jsonify(
                    termino = data['termino'],
                    que_es   = queEs,
                    causa  = causas
                )
        except Exception as e:
            return jsonify(
                    error = e
                )
    else:
        return 'nada que ver...med'
if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True , port = 5001)