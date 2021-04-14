from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
#from openpyxl import Workbook
#from openpyxl.writer.excel import save_virtual_workbook
#from scrapy.linkextractors import LinkExtractor


class DatosSerps(Item):
    url = Field()
    h1 = Field()
    h2 = Field()
    h3 = Field()
    title = Field()
    description = Field()
    preguntas_relacionadas = Field()
    busquedas_relacionadas = Field()

class SerpsGoogle(CrawlSpider):
    name = 'serp'

    pais = "es" #España
    num_resultados = ""
    busquedas = []
    start_urls_semillas = []    

    
    def __init__(self, *args, **kwargs):
        super(SerpsGoogle, self).__init__(*args, **kwargs)

       
        self.busquedas.append(str(kwargs['busqueda']))
        self.num_resultados = str(kwargs['num_resultados_serps'])

        print("\n\n\nLOS PARAMETROS DE BUSQUEDA SON:",self.busquedas)
        print("\n\n\nLOS PARAMETROS NUM RESULTADOS SON:",self.num_resultados)
        
        for self.busqueda in self.busquedas:
            self.start_urls_semillas.append('https://www.google.'+self.pais+'/search?q='+self.busqueda+'&num='+self.num_resultados)

        # URL SEMILLA
        self.start_urls = self.start_urls_semillas
    

    custom_settings = {
 
        "DOWNLOADER_MIDDLEWARES":{ #Necesito instalar la librería -> pip3 install Scrapy-UserAgents para rotar users agents automaticamente.
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
        },

        "USER_AGENTS": [
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/57.0.2987.110 '
            'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/61.0.3163.79 '
            'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
            'Gecko/20100101 '
            'Firefox/55.0')  # firefox
        ]

    }


    download_delay = 1
    




    
    def limpiartexto(self, texto):
     
        nuevoTexto = re.sub(r'<[^>]*>','',texto) #limpiar texto con expresiones regulares
        return nuevoTexto

   
    def parse(self, response):
        data = []        
        title = []
        h1 = []
        h2 = []
        h3 = []        
        description = []       
        preguntas_relacionadas = []
        busquedas_relacionadas = []
        ArrayURLSERPS = []

        sel = Selector(response)
        urlSerps = sel.xpath('//*[@id="center_col"]')
        item = ItemLoader(DatosSerps(), urlSerps)

        item.add_xpath('url', '//*[@id="rso"]/div/div/div/div/a/@href')
        item.add_xpath('description', '//*[@id="rso"]/div/div/div/div/span', MapCompose(self.limpiartexto)) 
        item.add_xpath('preguntas_relacionadas', '//g-accordion-expander/descendant::div/text()')
        item.add_xpath('busquedas_relacionadas', '//*[@id="w3bYAd"]/div/div/div/div/a/div[2]', MapCompose(self.limpiartexto))
        
        title = sel.xpath('//h3/text()').extract()
        item.add_value('title', title) 
        
        ArrayURLSERPS = item.get_collected_values('url') #Array de urls de la serps
        
        for x in range(0,len(ArrayURLSERPS)):
            try:
                reqs = requests.get(ArrayURLSERPS[x], timeout=5)			   
                soup = BeautifulSoup(reqs.text, 'lxml')
               
            except:
                continue
			
				
            for heading in soup.find_all(["h1", "h2", "h3"]):
                
					
                if(heading.name == "h1"):
                    h1.append(heading.text.strip())
                if(heading.name == "h2"):
                    h2.append(heading.text.strip())
                if(heading.name == "h3"):
                    h3.append(heading.text.strip())


        item.add_value('h1', h1)
        item.add_value('h2', h2)
        item.add_value('h3', h3)
        item.add_value('description', description)
        item.add_value('preguntas_relacionadas',preguntas_relacionadas)
        item.add_value('busquedas_relacionadas',busquedas_relacionadas)
        
        yield item.load_item()
        title = item.get_collected_values('title')
        description = item.get_collected_values('description')
        preguntas_relacionadas = item.get_collected_values('preguntas_relacionadas')
        busquedas_relacionadas = item.get_collected_values('busquedas_relacionadas')

        print("Importando datos...")    
		
        data = {
            'Title': title,
            'H1': h1,
            'H2': h2,
            'H3': h3,
            'Preguntas relacionadas': preguntas_relacionadas,
            'Búsquedas relacionadas': busquedas_relacionadas,
            'Descripción': description,
            'URL': ArrayURLSERPS
  
        }

        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.transpose()		
        #df = pd.DataFrame(data)
        df.to_excel("serp.xlsx")
        #print("\n\n LA TABLA ES: ", df)



#con process ejecuto scrapy automáticamente sin escribir -> scrapy crawl .....
#process = CrawlerProcess()
#process.crawl(SerpsGoogle)
#process.start()
#scrapy crawl serp -t json -o serp.json
