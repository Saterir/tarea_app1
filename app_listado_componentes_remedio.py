
from flask import Flask, redirect, url_for, request, render_template, jsonify
import sys
import os
import uuid
import urllib.request
from bs4 import BeautifulSoup
import re
import pymysql.cursors
import psycopg2

#usuario analitica
#contraseña 159753.analitica
#port 5432
#localhost

# INSERT INTO public.analitica(enfermedad, sintomas, url) VALUES ('prueba', 'pru', 'ba');
# cursor                  = PosgreSQL_DB_connect(DB_NAME,DB_USER,DB_HOST,DB_PASSWORD,DB_PORT)  
#                         query                   = "SELECT DISTINCT categoria FROM public.maestro_productos2 WHERE (descripcion like '%reciclable%' OR descripcion like '%gico%' OR descripcion like '%biodegradable%') AND sub_categoria = '"+SUB_CATEGORY+"' ORDER BY 1"
#                         query_response = Send_Query_To_DB(QUERY, DB_CONNECTION)

def Send_Query_To_DB(QUERY,CONNECTION):
    try:    
        CONNECTION.execute(QUERY)
        row = CONNECTION.fetchall()
        return row
    except Exception as e:
        return jsonify({'Error':"query error", 'Error_console':e})

def PosgreSQL_DB_connect(DB_NAME,DB_USER,DB_HOST,DB_PASSWORD,DB_PORT):
    try:
        connect_string = "dbname='"+DB_NAME+"' user='"+DB_USER+"' host='"+DB_HOST+"' password='"+DB_PASSWORD+"' port='"+DB_PORT+"'"
        connect = psycopg2.connect(connect_string)
        cursor = connect.cursor()
        return cursor
    except Exception as e:
        return jsonify({'Error':"database connection don't work", 'Error_console':e})

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
        Nota: para los " ", deben ser remplazados por "+" y todo debe estar en minuscula.
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
                if 'mg' in datos or '%' in datos or 'g' in datos:
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
        Nota: los espacios en blanco, se remplazan por "+" y se omiten los acentos.
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

@app.route('/buscarcompuesto', methods = ['GET','POST'])

def buscarcompuesto():
    data = None
    if request.method == 'POST':
        data = request.json
        try:
            url = urllib.request.urlopen("https://vsearch.nlm.nih.gov/vivisimo/cgi-bin/query-meta?v%3Aproject=medlineplus-spanish&v%3Asources=medlineplus-spanish-bundle&query="+data['compuesto']+"&_ga=2.158284350.541628268.1526482269-1655826678.1516816113")
            with url as fp:
                soup = BeautifulSoup(fp)
            if soup.find("ol", {"class": "results"}):
                soup = soup.find("ol", {"class": "results"})
                print(soup)
            soup = soup.find_all("li", {"class": "document source-drugs-spanish"})
            cont = 0
            for sopa in soup:
                sopa = sopa.find("span", {"class": "url"}).getText()
                #or "https://medlineplus.gov/spanish/druginfo/natural/" in sopa
                if "https://medlineplus.gov/spanish/druginfo/meds/" in sopa:
                    url  = urllib.request.urlopen(sopa)
                    #print(sopa)
                    with url as fp2:
                        soup2 = BeautifulSoup(fp2)
                    articulo = soup2.find("article")
                    articulo = articulo.find("div", {"id": "section-side-effects"})
                    articulo = BeautifulSoup(str(articulo).replace("<li>", "--"))
                    articulo = BeautifulSoup(str(articulo).replace("<h3>", "--|"))
                    #print(articulo)
                    # print(articulo)
                    # queEs  = soup2.find("div", {"id": "ency_summary"}).getText()
                    # causas = soup2.find("div", {"class": "section-body"}).getText()
                    cont += 1
                    #datos= articulo.text.split(':' ,1)[1]def challa(text):

                    def challa(text):
                        for i in text:
                            if i.isupper():
                                return str(text.split(i,1)[0])

                    datos= articulo.text.split(':' ,1)[1].split('--')
                    largo=len(datos)-1
                    datos[largo]=challa(datos[largo])
                    for i in range(len(datos)):
                        sacar=False
                        for k in range(len(datos[i])):
                            if (datos[i][k] == ':' or datos[i][k] =='|' ):
                                sacar=True
                        if(sacar==True):
                            datos[i]=''
                            #datos[i]=''

                    return jsonify(
                        termino = data['compuesto'],
                        datos=datos,
                    )

            if cont == 0:
                return jsonify(
                    termino = data['compuesto'],
                    resultado = "Ups.... Termino no encontrado en medlineplus"
                )

        except Exception as e:
            return jsonify(
                    error = e
                )
    else:
        return 'nada que ver...med'

@app.route('/busqueda_tesauro', methods = ['GET','POST'])

def busqueda_tesauro():
    # data = None
    # if request.method == 'POST':
    data = None
    if request.method == 'POST':
        data = request.json
        try:
            url = urllib.request.urlopen("https://www.freethesaurus.com/"+data['sintoma'])
            with url as fp:
                soup = BeautifulSoup(fp)
            soup = soup.find("section", {"data-src": "wn"}).getText()
            print(soup)    
            return jsonify(
                    error = "a"
                )
        except Exception as e:
            return jsonify(
                    error = e
                )
    else:
        return 'nada que ver...med'

@app.route('/busqueda_enfermedades', methods = ['GET','POST'])

def busqueda_enfermedades():
    DB_NAME     = 'datos'
    DB_USER     = 'analitica'
    DB_HOST     = 'localhost'
    DB_PASSWORD = '159753.analitica'
    DB_PORT     = '5432'
    data = None
    if request.method == 'POST':
        data = request.json
        try:
            az = ['A','B','C','D','F','G','H','I','J','L','M','O','P','R','S','T','U','V']
            for index in az:
                #print(index)
                url = urllib.request.urlopen("https://cuidateplus.marca.com/enfermedades/"+index+".html")
                #url = urllib.request.urlopen("https://cuidateplus.marca.com/enfermedades/A.html")
                with url as fp:
                    soup = BeautifulSoup(fp)
                links = soup.find("ul", {"class": "ul cuadruple-col"})
                links = links.find_all("a")
                for link_url in links:
                    name = link_url.getText()
                    print(name)
                    link = link_url.get('href')
                    link = urllib.request.urlopen(link)
                    with link as fp2:
                        sintomas = BeautifulSoup(fp2)
                    sintomas = sintomas.find("div", {"id": "sintomas"})
                    print(sintomas.getText())
                    print("--------------------------")
                    #sintomas = BeautifulSoup(str(sintomas).replace("<li>", "--"))
                    # sintomas = BeautifulSoup(str(sintomas).replace("'", " "))
                    # sintomas = BeautifulSoup(str(sintomas).replace('"', " "))
                    try:
                        connect_string = "dbname='"+DB_NAME+"' user='"+DB_USER+"' host='"+DB_HOST+"' password='"+DB_PASSWORD+"' port='"+DB_PORT+"'"
                        connect = psycopg2.connect(connect_string)
                        cursor = connect.cursor()
                        query = "INSERT INTO public.analitica(enfermedad, sintomas, url) VALUES (%s, %s, %s);"
                        datas = (name,str(sintomas.getText()),'a')
                        cursor.execute(query, datas)
                        connect.commit()
                        cursor.close()
                        connect.close()
                    except Exception as e:
                        pass
                    

            #soup = soup.find("section", {"data-src": "wn"}).getText()
            #print(soup)
            return jsonify(
                    status = 200
                )
        except Exception as e:
            return jsonify(
                    error = e
                )
    else:
        return 'nada que ver...med'
if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True , port = 5001)