#!/usr/bin/python3
 # -*- coding: utf-8 -*-
import subprocess
from flask import send_file, send_from_directory, safe_join, abort
from flask import Flask, render_template,request
from flask import Response
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

app = Flask(__name__)
	
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

queries = []
querie = ""

@app.route('/',methods=["GET"])
def inicio():
	
	return render_template("index.html")


@app.route('/espiar-competencia')
def upload_form():	
	return render_template("espiar-competencia.html")



@app.route('/espiar-competencia',methods=["GET"])
def espiar_competencia():
	return render_template('espiar-competencia.html')
	

@app.route('/descargar-productos-lista-asin',methods=["GET"])
def descargar_productos_lista_asin():
	return render_template('descargar-productos-lista-asin.html')


@app.route("/obtener-datos", methods=["post"]) #Ejecuta la araña y la muestra en la pagina /obtener-datos
def serps():
	querie = request.form.get("queries")
	num_serps = request.form.get("num_serps")
	pais = request.form.get("pais")
	idioma = request.form.get("idioma")
	motor = request.form.get("motor")

	print("Consulta: "+querie)
	print("Num búsquedas: "+num_serps)
	print("País: "+pais) #gl=ES 
	print("Idioma: "+idioma) #hl=es
	print("Motor: "+motor)


	spider_name = "serp"

	    
	subprocess.check_output(['scrapy', 'crawl', spider_name, '-a', f'busqueda={querie}', '-a', f'num_resultados_serps={num_serps}', '-a',  f'motor={motor}', '-a',  f'pais={pais}', '-a',  f'idioma={idioma}'])	
	
	return render_template("obtener-datos.html", datos=request.form)


@app.route('/download')
def download_file():
	
	path = "file.xlsx"	
	return send_file(path, as_attachment=True)
	








if __name__ == '__main__':
    app.run(port=5000)
