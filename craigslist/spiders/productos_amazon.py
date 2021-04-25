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
import requests
import json
from deepl import deepl


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
    asins = Field()
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
    start_urls = []
    asins = []

    codigo_afiliado = ""
    traducir_texto = ""
    idioma_actual = ""
    paso_idioma_1 = ""
    paso_idioma_2 = ""
    translated_descripcion = []



    def __init__(self, *args, **kwargs):
        super(StackOverflowSpider, self).__init__(*args, **kwargs)

        #asins = ["B000MWR59A", "B01ELDCSHY","B07PXTB77V"]
        
       
        asin = kwargs['asins']
        self.asins = re.split(', |,|; |;|\n', asin)

        pais_tienda = kwargs['pais_tienda'] #Tienda de amazon, España, USA, etc.
        self.codigo_afiliado = kwargs['codigo_afiliado']
        self.traducir_texto = kwargs['traducir_texto']
        self.idioma_actual = kwargs['idioma_actual']
        self.paso_idioma_1 = kwargs['paso_idioma_1']
        self.paso_idioma_2 = kwargs['paso_idioma_2']


        for asn in self.asins:
            # URL SEMILLA
            self.start_urls.append('https://www.'+pais_tienda+'/dp/'+asn)

    custom_settings = {
 
        "DOWNLOADER_MIDDLEWARES":{ #Necesito instalar la librería -> pip3 install Scrapy-UserAgents para rotar users agents automaticamente.
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
        },

        "USER_AGENTS": [
            ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0'),
            ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'),
            ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.36 Safari/537.36'),  # chrome
            ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'),  # chrome
            ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36')  # firefox

            
        ]

    }
    
    
    
    


    download_delay = 1


    def translate_text_deepl(self, data, idioma1, idioma2):
        self.translated_descripcion = []
        
        t = deepl.DeepLCLI(langs=(idioma1, idioma2))
        
        for texto in data:    
            self.translated_descripcion.append(t.translate(texto))
        
        return self.translated_descripcion 



    


    def quitarsaltolinea(self, texto):
        nuevoTexto = texto.replace("\n", "").replace("€", "").replace("[]", "").replace(" de 5 estrellas", "")
        return nuevoTexto

    def limpiarNum_reviews(self, texto):
        nuevoTexto = texto.replace("\n", "").replace("[]", "").replace(" valoraciones", "").replace(".", "")
        return nuevoTexto


    def limpiarDescripcion(self, texto):

        for t in texto:
            t = re.sub("\n","",texto) #limpiar texto con expresiones regulares
        return t

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


        
        print("asins", self.asins)   
        print("codigo_afiliado: ",self.codigo_afiliado)
        print("traducir_texto: ",self.traducir_texto)
        print("idioma_actual: ",self.idioma_actual)
        print("paso_idioma_1: ",self.paso_idioma_1)
        print("paso_idioma_2: ",self.paso_idioma_2)
       

        # Selectores: Clase de scrapy para extraer datos
        sel = Selector(response)
        producto = sel.xpath('//*[@id="ppd"]')

        item = ItemLoader(DetalleProducto(), producto)
        
        def check_exists_by_xpath(xpath):
            
            if((str(xpath) != "None") or (str(xpath) == "")): #Si el producto tiene el precio rebajado
                return xpath         

            else:
                xpath = ""
                return xpath
                          
   

        try:
            item.add_value('image', check_exists_by_xpath(re.search('"large":"(.*?)"',response.text).groups()[0]))
        except:
            item.add_value('image', '')

        try:
            item.add_value('marca', check_exists_by_xpath(producto.xpath('//span[normalize-space()="Marca"]/following::span/text()').extract_first()))
        except:
            item.add_value('marca', '')

        try:
            item.add_xpath('titulo_producto',check_exists_by_xpath('.//*[@id="productTitle"]/text()'), MapCompose(self.quitarsaltolinea))
        except:
            item.add_xpath('titulo_producto','')

        try:
            item.add_xpath('precio',check_exists_by_xpath('.//*[@id="priceblock_ourprice" or @id="priceblock_saleprice" or @id="priceblock_dealprice"]//text()'), MapCompose(self.quitarsaltolinea))
        except:
            item.add_xpath('precio','')

        try:
            item.add_value('precio_caro', check_exists_by_xpath(producto.xpath('.//*[@class="priceBlockStrikePriceString a-text-strike"]/text()').extract_first()), MapCompose(self.quitarsaltolinea)) #si devuelve "None" lo cambio por "" y sino devuelvo el valor del precio.
        except:
            item.add_value('precio_caro', '')

        try:
            item.add_xpath('num_reviews',check_exists_by_xpath('.//*[@id="acrCustomerReviewText"]/text()'), MapCompose(self.limpiarNum_reviews))
        except:
            item.add_xpath('num_reviews','')

        try:
            item.add_xpath('estrellas', check_exists_by_xpath('.//*[@id="acrPopover"]/@title'), MapCompose(self.quitarsaltolinea))
        except:
            item.add_xpath('estrellas', '')

        try:
            item.add_xpath('descripcion', check_exists_by_xpath('.//*[@id="feature-bullets"]//*[@class="a-list-item"]/text()'), MapCompose(self.limpiarDescripcion))
        except:
            item.add_xpath('descripcion', '')

     

        yield item.load_item()


        try:
            imagen.append(item.get_collected_values('image')[0])
        except:
            imagen.append("")

        try:
            marca.append(item.get_collected_values('marca')[0])
        except:
            marca.append("")

        try:
            titulo_producto.append(item.get_collected_values('titulo_producto')[0])
        except:
            titulo_producto.append("")

        try:
            precio.append(item.get_collected_values('precio')[0])
        except:
            precio.append("")

        try:
            precio_caro.append(item.get_collected_values('precio_caro')[0])
        except:
            precio_caro.append("")
      
        try:
            num_reviews.append(item.get_collected_values('num_reviews')[0])
        except:
            num_reviews.append("")

        try:
            estrellas.append(item.get_collected_values('estrellas')[0])
        except:
            estrellas.append("")

        try:
          
            descripcion.append('\n\n'.join([str(elem) for elem in item.get_collected_values('descripcion')])) #convierto array con varios elementos en array con un único elemento para que se guarde en la misma casilla excel
            print("\n\n\nDESCRIPCION FORMATEADA ES: ", descripcion[0],"\n\n\n")
            
           
        except:
            descripcion.append("")

        if(self.traducir_texto == "si"):
            self.translate_text_deepl(descripcion, self.idioma_actual, self.paso_idioma_1)
            self.translate_text_deepl(self.translated_descripcion, self.paso_idioma_1, self.paso_idioma_2) 
            self.translate_text_deepl(self.translated_descripcion, self.paso_idioma_2, self.idioma_actual)
              
            #self.translate_text_deepl(descripcion, "8f63242b-6f86-2229-7f47-a74db99fb508:fx", src_lang=self.idioma_actual, target_lang=self.paso_idioma_1)
            #self.translate_text_deepl(self.translated_descripcion, "8f63242b-6f86-2229-7f47-a74db99fb508:fx", src_lang=self.paso_idioma_1, target_lang=self.paso_idioma_2)
            #self.translate_text_deepl(self.translated_descripcion, "8f63242b-6f86-2229-7f47-a74db99fb508:fx", src_lang=self.paso_idioma_2, target_lang=self.idioma_actual)
            print("\n\n\n\nTraducción: ", self.translated_descripcion,"\n\n\n\n")
        print("Importando datos...")  
         
		
        data = {
            'asins': self.asins,
            'Imagen': imagen,
            'Marca': marca,
            'Título producto': titulo_producto,            
            'Precio': precio,
            'Precio caro': precio_caro,
            'Nún reviews': num_reviews,
            'Estrellas': estrellas,
            'Descripcion': descripcion,
            'Descripcion traducida': self.translated_descripcion

        }

        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.transpose()		
        #df = pd.DataFrame(data)
        df.to_excel("file.xlsx")
            

        
        
      
# EJECUCION EN TERMINAL:
# scrapy crawl productos_amazon -a asins="B000MWR59A" -a pais_tienda="amazon.es" -a codigo_afiliado="bbpromo-21" -a traducir_texto="si" -a idioma_actual="es" -a paso_idioma_1="en" -a paso_idioma_2="pt" -t json -o productos_amazon.json
# scrapy crawl productos_amazon -a asins="B000MWR59A" -a pais_tienda="amazon.es" -a codigo_afiliado="bbpromo-21" -a traducir_texto="si" -a idioma_actual="ES" -a paso_idioma_1="EN" -a paso_idioma_2="RU" -t json -o productos_amazon.json