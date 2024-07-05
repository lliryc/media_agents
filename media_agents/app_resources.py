import os
from media_agents.config import RESOURCES_ROOT_DIR
# Default locale setting
app_locale = 'en'  # Default locale

def set_locale(locale_name):
    """
    Set the application locale.

    :param locale_name: The locale name to be set (e.g., 'en', 'de', 'ar', etc.)
    """
    global app_locale
    app_locale = locale_name

def get_locale():
    """
    Get the current application locale.

    :return: The current locale name
    """
    global app_locale
    return app_locale

def get_resource_content(res_file_path):
    """
    Get the content of a resource file for the current locale.

    :param res_file_path: The path to the resource file, relative to the locale directory
    :return: The content of the resource file as a string
    """
    global app_locale
    path = os.path.join(RESOURCES_ROOT_DIR, app_locale, res_file_path)
    with open(path, 'r', encoding='utf8') as fh:
        content = fh.read()
    return content