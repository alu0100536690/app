#!/usr/bin/python3
 # -*- coding: utf-8 -*-
from flask import send_file, send_from_directory, safe_join, abort
from flask import Flask, render_template,request
from flask import Response
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
import requests
import string
import urllib
from bs4 import BeautifulSoup
import re
import pandas as pd
from pathlib import Path
import time

app = Flask(__name__)
	
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

queries = []
querie = ""

@app.route('/')
def upload_form():
	return render_template('formulario.html')

@app.route('/download')
def download_file():
	
	path = "serps.xlsx"	
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
	
	
	
	
	if querie != "":
	
		
		queries.append(querie)
		
		#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
		print("La querie es: "+queries[0])
		print("El numero es: "+num_serps)
		

		  
		#queries = data['queries']
		url = "https://www.google.es/search"
		country = "ES"
		serp_queries = []
		serp_urls = []
		clean_links = []
		links = []
		serp_titles = []
		serp_descriptions = []
		h1 = []
		h2 = []
		h3 = []


		for q in queries:
			query = urllib.parse.quote_plus(q)
			serp_queries.append(query)

		for q in serp_queries:
			url = "{base_url}?q={query}&num={num}&cr={serp_country}".format(base_url = url, query=q, num = num_serps, serp_country = country)
			serp_urls.append(url)
			response = requests.get(url)
			soup = BeautifulSoup(response.text, "lxml")
			result_div = soup.find_all('div', attrs = {'class': 'ZINbbc'})
			for r in result_div:
				# Checks if each element is present, else, raise exception
				try:
				    link = r.find('a', href = True)
				    title = r.find('div', attrs={'class':'vvjwJb'}).get_text()
				    description = r.find('div', attrs={'class':'s3v9rd'}).get_text()
				    # Check to make sure everything is present before appending
				    if link != '' and title != '' and description != '': 
				        links.append(link['href'])
				        serp_titles.append(title)
				        serp_descriptions.append(description)
				# Next loop if one element is not present
				except:
				    continue
			to_remove = []
			
		for i, l in enumerate(links):
			try:
				clean = re.search('\/url\?q\=(.*)\&sa',l)

				# Anything that doesn't fit the above pattern will be removed
				if clean is None:
					to_remove.append(i)
					continue
				clean_links.append(clean.group(1))
			except:
				continue
		 
		   
		for x in range(0,len(clean_links)):
			try:
				reqs = requests.get(clean_links[x], timeout=5)			   
				soup = BeautifulSoup(reqs.text, 'lxml')
				#print(soup)
			except:
				continue
			
				
			for heading in soup.find_all(["h1", "h2", "h3"]):
					
				if(heading.name == "h1"):
					h1.append(heading.text.strip())
				if(heading.name == "h2"):
					h2.append(heading.text.strip())
				if(heading.name == "h3"):
					h3.append(heading.text.strip())

		
			   
		 
		print("Importando datos...")    
		import pandas as pd
		data = {'Title': serp_titles,
				'H1': h1,
				'H2': h2,
				'H3': h3,
				'Description': serp_descriptions,		
				'URLs': clean_links}
		df = pd.DataFrame.from_dict(data, orient='index')
		df = df.transpose()

		#df.to_excel(queries[0]+'.xlsx', sheet_name='SERPS')
		df.to_excel('serps.xlsx', sheet_name='SERPS')
		print("Datos importados correctamente")
		filexls = queries[0]
		queries.clear()
		querie = ""
		#return send_file(filexls+".xlsx", as_attachment=True)
		

			
		return render_template("datos.html", datos=request.form)
	else:
	    #pass
		return render_template("error.html", error="Contraseña incorrecta")



if __name__ == '__main__':
    app.run(port=5000)
