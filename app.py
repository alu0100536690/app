import os
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
def productos_lista_asin():
	return render_template('descargar-productos-lista-asin.html')



@app.route("/obtener-datos-productos-amazon", methods=["post"]) 
def descargar_productos_lista_asin():
	asins = request.form.get("asins")
	pais_tienda = request.form.get("pais_tienda")
	codigo_afiliado = request.form.get("codigo_afiliado")
	traducir_texto = request.form.get("traducir_texto")
	idioma_actual = request.form.get("idioma_actual")
	paso_idioma_1 = request.form.get("paso_idioma_1")
	paso_idioma_2 = request.form.get("paso_idioma_2")

	spider_name = "productos_amazon"

	                                                                                                   
																									                                                                   	    
	subprocess.check_output(['scrapy', 'crawl', spider_name, '-a', f'asins={asins}', '-a', f'pais_tienda={pais_tienda}', '-a', f'codigo_afiliado={codigo_afiliado}', '-a', f'traducir_texto={traducir_texto}', '-a', f'idioma_actual={idioma_actual}', '-a', f'paso_idioma_1={paso_idioma_1}', '-a', f'paso_idioma_2={paso_idioma_2}'])	
	return render_template("obtener-datos.html", datos=request.form)
	#Ejemplo ejecutar araña descargar productos lista asin:
	#scrapy crawl productos_amazon -a asins="B000MWR59A, B01ELDCSHY" -a pais_tienda="amazon.es" -a codigo_afiliado="bbpromo-21" -a traducir_texto="si" -a idioma_actual="ES" -a paso_idioma_1="US" -a paso_idioma_2="RU" -t json -o productos_amazon.json

@app.route("/obtener-datos-google", methods=["post"]) 
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
	


port = int(os.environ.get("PORT", 5000))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=port)
