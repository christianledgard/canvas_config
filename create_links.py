import datetime
from datetime import timedelta
import requests
import json

course               = '4173'
course_cod           = 'EG0008'
course_name          = 'Proyecto Interdisciplinario II'
course_section       = '41' #CURSO-SECCIÓN
course_profesor      = 'Jesus Bellido Angulo'
course_type          = 'Teoria' #"TIPO [Teoría|Labotorio]:")
course_starts        = '09:00'  #input("HORA INICIO: HH:mm ")
course_ends          = '11:00'  #input("HORA FIN: HH:mm ")
dia                  = 6        #primer día de clases en Abril.
zoom_url             = ''#input("LINK ZOOM:")
first_week           = 1
last_week            = 16
# Buscar el token de acceso en https://utec.instructure.com/profile/settings
# Entrar en Integraciones aprobadas
# +Nuevo Token de Acceso
# Ejemplo: '4689~tPwx4RGnTyFV7XuochO1gWtFap9jPeW7KfsjBz6IDr0HIUUY6lQnstSsghMGMNwH'
access_token   = ''
is_visible_videoconf = True
is_visible_headers   = True
is_visible_links     = True

#CONNECTOR
url_course = '<path>/<course>'
url_modules = '<path>/<course>/modules?per_page=40'
url_items = '<path>/<course>/modules/<module>/items'
path = 'https://utec.instructure.com/api/v1/courses'

def headers():
    token = 'Bearer '+access_token
    return {'Authorization': token}

def get(url):
    url = url.replace('<path>', path)
    r = requests.get(url, headers = headers())
    if r.status_code >= 400:
        raise Exception("Unauthorized, Verify course and access_token")

def post(url, data):
    url = url.replace('<path>', path)
    r = requests.post(url, headers = headers(), data = data)
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
    return  post(url, item)

def fomatear_titulo( dia, mes, semana, prefix ='' ):
    f = '<prefix>2020-1 <course_cod> ES <course_name>, <course_section>, Semana<course_semana>, <course_profesor>, <course_mes>/<course_dia>, <course_starts> - <course_ends> <course_type>'
    f = f.replace('<course_cod>', course_cod)
    f = f.replace('<course_name>', course_name)
    f = f.replace('<course_section>', course_section)
    f = f.replace('<course_mes>', mes)
    f = f.replace('<course_dia>', dia)
    f = f.replace('<course_starts>', course_starts)
    f = f.replace('<course_ends>', course_ends)
    f = f.replace('<course_semana>', semana)
    f = f.replace('<course_profesor>', course_profesor)
    f = f.replace('<course_type>', course_type)
    f = f.replace('<prefix>', prefix)
    return f

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
        prefixes = ['Grabación ','']
        for prefix in prefixes:
            data = {}
            data['module_item[title]'] = fomatear_titulo( date.strftime("%d"), date.strftime("%m"), "{:02d}".format(i), prefix=prefix)
            data['module_item[type]'] = 'ExternalUrl'
            data['module_item[position]'] = '1'
            data['module_item[indent]'] = '1'
            data['module_item[external_url]'] = zoom_url
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



#print(modules)
