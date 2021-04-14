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

@app.route('/')
def upload_form():
	return render_template('formulario.html')

@app.route('/download')
def download_file():
	
	path = "serp.xlsx"	
	return send_file(path, as_attachment=True)
	
	
@app.route('/',methods=["GET"])
def inicio():
	
	return render_template("formulario.html")

@app.route("/", methods=["post"])

def procesar_formulario():
	querie = request.form.get("queries")
	num_serps = request.form.get("num_serps")

	print("Consulta: "+querie)
	print("Num búsquedas: "+num_serps)

	spider_name = "serp"
	subprocess.check_output(['scrapy', 'crawl', spider_name, '-a', f'busqueda={querie}', '-a', f'num_resultados_serps={num_serps}'])	
	#subprocess.check_output(['crawl', spider_name, '-a', f'busquedas={querie}', '-a', f'num_resultados={num_serps}' ]) 
	return render_template("datos.html", datos=request.form)

	


if __name__ == '__main__':
    app.run(port=5000)
