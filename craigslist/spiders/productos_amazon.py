# -*- coding: utf-8 -*-
from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.loader import ItemLoader
import re

import pandas as pd
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

imagen = []
marca = []
titulo_producto = []
precio = []
precio_caro = []
num_reviews = []
estrellas = []
descripcion = []

# ABSTRACCION DE DATOS A EXTRAER - DETERMINA LOS DATOS QUE TENGO QUE LLENAR Y QUE ESTARAN EN EL ARCHIVO GENERADO
class DetalleProducto(Item):
    image = Field()
    titulo_producto = Field()
    marca = Field()
    precio = Field()
    precio_caro = Field()
    descripcion = Field()
    num_reviews = Field()
    estrellas = Field()
    
    

# CLASE CORE - SPIDER
class StackOverflowSpider(Spider):
    name = "productos_amazon" # nombre, puede ser cualquiera 
    
    # Forma de configurar el USER AGENT en scrapy
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36'
    }    
    
    
    pais = "es" #España
    asins = ["B000MWR59A", "B01ELDCSHY","B07PXTB77V"]
    start_urls_semillas = []

    for asin in asins:
        start_urls_semillas.append('https://www.amazon.'+pais+'/dp/'+asin)
    print("ASIN DE PRODUCTOS: ",start_urls_semillas)    
   
    # URL SEMILLA
    start_urls = start_urls_semillas


    
    def quitarsaltolinea(self, texto):
        nuevoTexto = texto.replace("\n", "").replace("€", "")
        return nuevoTexto

    #Funcion que se va a llamar cuando se haga el requerimiento a la URL semilla
    def parse(self, response):
        
        global imagen
        global marca
        global titulo_producto
        global precio
        global precio_caro
        global num_reviews
        global estrellas
        global descripcion
       

        # Selectores: Clase de scrapy para extraer datos
        sel = Selector(response)
        producto = sel.xpath('//*[@id="ppd"]')

        item = ItemLoader(DetalleProducto(), producto)
        
        def check_exists_by_xpath(xpath): 
            
            if(str(xpath) != "None"): #Si el producto tiene el precio rebajado               
                #precio_caro.append(xpath)
                return xpath         

            else:
                #precio_caro.append("")
                xpath = ""
                return xpath
                          
   
        
        item.add_value('image', re.search('"large":"(.*?)"',response.text).groups()[0])
        item.add_value('marca', producto.xpath('//span[normalize-space()="Marca"]/following::span/text()').extract_first())
        item.add_xpath('titulo_producto','.//*[@id="productTitle"]/text()', MapCompose(self.quitarsaltolinea))
        item.add_xpath('precio','.//*[@id="priceblock_ourprice"]/text()', MapCompose(self.quitarsaltolinea))

        valorprecio_caro = producto.xpath('.//*[@class="priceBlockStrikePriceString a-text-strike"]/text()').extract_first()
        item.add_value('precio_caro', check_exists_by_xpath(valorprecio_caro), MapCompose(self.quitarsaltolinea)) #si devuelve "None" lo cambio por "" y sino devuelvo el valor del precio.

        item.add_xpath('num_reviews','.//*[@id="acrCustomerReviewText"]/text()')
        item.add_xpath('estrellas', './/*[@id="acrPopover"]/@title')
        item.add_xpath('descripcion', './/*[@id="feature-bullets"]//*[@class="a-list-item"]/text()', MapCompose(self.quitarsaltolinea))

        yield item.load_item()



        imagen.append(item.get_collected_values('image')[0])
        marca.append(item.get_collected_values('marca')[0])        
        titulo_producto.append(item.get_collected_values('titulo_producto')[0])
        precio.append(item.get_collected_values('precio')[0])
        precio_caro.append(item.get_collected_values('precio_caro')[0])       
        num_reviews.append(item.get_collected_values('num_reviews')[0])
        estrellas.append(item.get_collected_values('estrellas')[0])
        descripcion.append(item.get_collected_values('descripcion')[0])

        print("Importando datos...")    
		
        data = {
            'Imagen': imagen,
            'Marca': marca,
            'Título producto': titulo_producto,
            'Precio': precio,
            'Precio caro': precio_caro,
            'Nún reviews': num_reviews,
            'Estrellas': estrellas,
            'Descripcion': descripcion

        }

        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.transpose()		
        #df = pd.DataFrame(data)
        df.to_excel("file.xlsx")
            

        
        
      
# EJECUCION EN TERMINAL:
# scrapy runspider productos_amazon.py -t csv -o productos_amazon.csv
#scrapy crawl productos_amazon -t json -o productos_amazon.json