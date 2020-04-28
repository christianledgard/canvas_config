import datetime
from datetime import timedelta
import requests
import json

#####################################################################################################
#                                   Just config your course here                                    #
course               = '4395'   # From Canvas
course_cod           = 'CS2B01' # From our curricula at the university
course_name          = 'Desarrollo Basado en Plataformas'
course_section       = '2' #CURSO-SECCIÓN
course_abrv          = 'DBP' #Abbreviations
course_professor     = 'Jesus Bellido'
course_type          = 'Teoria' #"TIPO [Teoría|Labotorio]:")
course_starts        = '18:00'  #input("HORA INICIO: HH:mm ")
course_ends          = '20:00'  #input("HORA FIN: HH:mm ")
dia                  = 9        #primer día de clases en Abril.
zoom_url             = 'https://zoom.us/j/666900335'       #input("LINK ZOOM:")
slides_url           = 'http://bit.ly/2QrMkyU'      #OPCIONAL- input("LINK SLIDES:")
first_week           = 16        # from this week
last_week            = 16        # until this week
access_token         = ''
print('===========================================================')
print('Revisar https://utec.instructure.com/profile/settings      ')
print('Entrar en Integraciones aprobadas -> +Nuevo Token de Acceso')
access_token         = input('Ingresa tu token (ej: 4689~tPwx4RGnTyFV7XuochO1gWtFap9jPeW7KfsjBz6IDr0HIUUY6lQnstSsghMGMNwH): ')
is_visible_videoconf = True # Add label for Videoconferencia
is_visible_headers   = True # Add labels for Mayterial de Clase & Actividades
is_visible_links     = True # Create links for Videoconferencia and Grabacion
is_visible_links_of_slides  = False # Create links for Index of Chapters

#####################################################################################################
#CONNECTOR
url_course  = '<path>/<course>'
url_modules = '<path>/<course>/modules?per_page=40'
url_items   = '<path>/<course>/modules/<module>/items'
path        = 'https://utec.instructure.com/api/v1/courses'

def headers():
    token = 'Bearer '+access_token
    return {'Authorization': token}

def get(url):
    url = url.replace('<path>', path)
    r = requests.get(url, headers = headers())
    if r.status_code >= 400:
        raise Exception("Unauthorized, Verify course and access_token")
    return r.json()

def post(url, data):
    url = url.replace('<path>', path)
    r = requests.post(url, headers = headers(), data = data)
    if r.status_code >= 400:
        raise Exception("Unauthorized, Verify course and access_token")
    return r.json()

def get_modules(course):
    url = url_modules
    url = url.replace('<course>', course)
    return get(url)

def get_items(course, module):
    url = url_items
    url = url.replace('<course>', course)
    url = url.replace('<module>', str(module))
    return get(url)

def post_item(course, module, item):
    url = url_items
    url = url.replace('<course>', course)
    url = url.replace('<module>', str(module))
    #print(item)
    return  post(url, item)

def format_title( dia, mes, semana, prefix ='' ):
    format = '<prefix>2020-1 <course_cod> ES <course_name>, <course_section>, Semana<course_semana>, <course_professor>, <course_mes>/<course_dia>, <course_starts> - <course_ends> <course_type>'
    format = format.replace('<course_cod>', course_cod)
    format = format.replace('<course_name>', course_name)
    format = format.replace('<course_section>', course_section)
    format = format.replace('<course_mes>', mes)
    format = format.replace('<course_dia>', dia)
    format = format.replace('<course_starts>', course_starts)
    format = format.replace('<course_ends>', course_ends)
    format = format.replace('<course_semana>', semana)
    format = format.replace('<course_professor>', course_professor)
    format = format.replace('<course_type>', course_type)
    format = format.replace('<prefix>', prefix)
    return format

def create_header(course, module, titulo):
    data = {}
    data['module_item[title]'] = titulo
    data['module_item[type]'] = 'SubHeader'
    data['module_item[position]'] = '1'
    data['module_item[indent]'] = '0'
    new_item = post_item(course, module, data)


def configure_week(module_id, date):

    date_start = date - timedelta(days=date.weekday())
    date_end = date_start + timedelta(days=6)
    #items = get_items(course, module['id'])
    if is_visible_videoconf:
        h = "Videoconferencia - Semana <start_mes>/<start_dia> - <end_mes>/<end_dia>"
        h = h.replace('<start_dia>',date_start.strftime("%d") )
        h = h.replace('<start_mes>',date_start.strftime("%m") )
        h = h.replace('<end_dia>',date_end.strftime("%d") )
        h = h.replace('<end_mes>',date_end.strftime("%m") )
        create_header(course, module_id, h)

    if is_visible_headers:
        create_header(course, module_id, 'Actividades')
        create_header(course, module_id, 'Material de clase')

    if is_visible_links:
        prefixes = [('Grabación ', 'http://tu_grabacion_en_zoom.com'),('', zoom_url)]
        for prefix, url in prefixes:
            data = {}
            data['module_item[title]'] = format_title( date.strftime("%d"), date.strftime("%m"), "{:02d}".format(i), prefix=prefix)
            data['module_item[type]'] = 'ExternalUrl'
            data['module_item[position]'] = '1'
            data['module_item[indent]'] = '1'
            data['module_item[external_url]'] = url
            data['module_item[new_tab]'] = 1

            new_item = post_item(course, module_id, data)

    if is_visible_links_of_slides:
        title = "[SLIDES] Index of Chapters - <abrev>"
        title = title.replace('<abrev>', course_abrv)

        data = {}
        data['module_item[title]'] = title
        data['module_item[type]'] = 'ExternalUrl'
        data['module_item[position]'] = '1'
        data['module_item[indent]'] = '1'
        data['module_item[external_url]'] = slides_url
        data['module_item[new_tab]'] = 1

        new_item = post_item(course, module_id, data)


first_date = datetime.datetime(2020, 4, dia)
delta = timedelta(days = 7)

i = 0
for module in  get_modules(course):
    if module['name'].startswith('Semana '):
        i += 1
        if i >= first_week and i <= last_week :
            print("Configuring", module['name'])
            configure_week(module['id'], first_date)
        first_date = first_date + delta
print('It seams we finished ... please REFRESH your browser to see to new configuration !')
print('This small program was created by Jesus Bellido <jbellido@utec.edu.pe>')

#print(modules)
