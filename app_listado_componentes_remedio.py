
from flask import Flask, redirect, url_for, request, render_template, jsonify
import sys
import os
import uuid
import urllib.request
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/remedio', methods = ['GET','POST'])

def remedio():
    """
        Funcion encargada de buscar un remedio especifico en la base de datos de laboratorio chile
        entrada:

        {
            "remedio": "Aciclovir"
        }

        salida:

        {
            "compuesto": "Aciclovir",
            "remedio": "Aciclovir"
        }

    """
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

@app.route('/buscarterminomedico', methods = ['GET','POST'])

def buscarterminomedico():
    """
        Funcion que permite buscar terminos atomicos en la enciclopedia médica de medlineplus
        el json de entrado es de la siguiente forma:
        
        {
	        "termino":"Queloides"
        }    

        la salida es de la forma:

        {
            "causa": "Los queloides se pueden formar después de lesiones de la piel a raíz de:AcnéQuemadurasVaricelaPerforaciones en las orejasLaceraciones menoresCortes por cirugía o traumatismoSitios de vacunasLos queloides son más común en personas menores de 30 años. Los afroamericanos, los asiáticos y los hispanos son más propensos a desarrollar queloides. A menudo se transmiten de padres a hijos. A veces una persona puede desconocer cuál lesión provocó que se formara el queloide.",
            "que_es": "Es el crecimiento de tejido cicatricial adicional. Se presenta en donde la piel ha sanado después de una lesión.",
            "termino": "Queloides"
        }
    """
    data = None
    if request.method == 'POST':
        data = request.json
        try:
            url = urllib.request.urlopen("https://vsearch.nlm.nih.gov/vivisimo/cgi-bin/query-meta?v%3Aproject=medlineplus-spanish&v%3Asources=medlineplus-spanish-bundle&query="+data['termino']+"&_ga=2.158284350.541628268.1526482269-1655826678.1516816113")
            with url as fp:
                soup = BeautifulSoup(fp)
            soup = soup.find("ol", {"class": "results"})
            soup = soup.find_all("li", {"class": "document source-medical-sites-spanish"})
            #print (soup[0])
            cont = 0
            for sopa in soup:
                sopa = sopa.find("span", {"class": "url"}).getText()
                if "https://medlineplus.gov/spanish/ency/article" in sopa:
                    url  = urllib.request.urlopen(sopa)
                    with url as fp2:
                        soup2 = BeautifulSoup(fp2)
                    queEs  = soup2.find("div", {"id": "ency_summary"}).getText()
                    causas = soup2.find("div", {"class": "section-body"}).getText()
                    cont += 1

                    return jsonify(
                        termino = data['termino'],
                        que_es  = queEs,
                        causa   = causas
                    )

            if cont == 0:
                return jsonify(
                    termino = data['termino'],
                    resultado = "Ups.... Termino no encontrado en medlineplus"
                )

        except Exception as e:
            return jsonify(
                    error = e
                )
    else:
        return 'nada que ver...med'
if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True , port = 5001)