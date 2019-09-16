#library for getting the current datetime for printing in the report
from datetime import datetime
import plotly
import requests
#library for creating the template
import jinja2
#lib for create pdf
import pdfkit

import plotly.graph_objects as go


class Report:

    def __init__(self, lat_1, long_1, lat_2, long_2, result_1, result_2, graph_1, result_3 = None, graph_2 = None):
        self.lat_1 = lat_1
        self.long_1 = long_1
        self.lat_2 = lat_2
        self.long_2 = long_2
        self.result_1 = result_1
        self.result_2 = result_2
        self.result_3 = result_3
        self.graph_1 = graph_1
        self.graph_2 = graph_2
    
    #method for make the reverse geocoding request and return the place
    def make_request(self):
        r_url = "https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}&zoom=10".format(self.lat_1, self.long_1)
        r = requests.get(url = r_url)
        data = r.json()
        return data['display_name']

    def generateTemplate(self):
       #create the date (formatted) that will appear on the report
        report_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        #create the date that will be on the html file form avoid concurrent conflicts
        graph_date = datetime.now().strftime("%b%d%Y%H%M%S")
        #change graph colors
        graph_colors = ['rgb(31,119,180)', 'rgb(255,127,14)']

        #verifying if is image analysis case
        image_analysis_flag = True if self.result_3 is None else False

        #download the report plot
       
        graph_png_1 = go.Figure(self.graph_1)
        graph_png_1.write_image("generated_figures/{}_1.png".format(graph_date))

        if not image_analysis_flag:
            graph_png_2 = go.Figure(self.graph_2)
            graph_png_2.write_image("generated_figures/{}_2.png".format(graph_date))


        #reverse geocoding
        localization = self.make_request()

        #loading the template
        #code from = http://www.marknagelberg.com/creating-pdf-reports-with-python-pdfkit-and-jinja2-templates/
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "report_template.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        
        
        parameters = template.render(date = report_date, localization = localization, result_1 = self.result_1, graph_1 = graph_date, graph_2 = graph_date,  result_2 = self.result_2, result_3 = self.result_3, lat_1 = self.lat_1, long_1 = self.long_1, lat_2 = self.lat_2, long_2 = self.long_2, flag = image_analysis_flag)
         
        html_file = open("generated_html/{}_html_report.html".format(graph_date), 'w')
        html_file.write(parameters)
        html_file.close()

        #converting and writing into pdf
        
        config = pdfkit.configuration(wkhtmltopdf=bytes('C://Program Files//wkhtmltopdf//bin//wkhtmltopdf.exe', 'utf-8'))
        pdfkit.from_file("generated_html/{}_html_report.html".format(graph_date), "generated_pdf\{}_reporte.pdf".format(graph_date), configuration = config)
        return graph_date
