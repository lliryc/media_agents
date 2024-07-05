import os
app_locale = 'en' # locale by default

def set_locale(locale_name): # en, de, ar, ..
    global app_locale
    app_locale = locale_name

def get_locale():
    global app_locale
    return app_locale

RESOURCES_ROOT_DIR = '../resources'
def get_resource_content(res_file_path):
    path = os.path.join(RESOURCES_ROOT_DIR, app_locale, res_file_path)
    with open(path, 'r', encoding='utf8') as fh:
        content = fh.read()
    return content