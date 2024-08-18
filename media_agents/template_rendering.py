import json
import datetime
import jsonlines
from jinja2 import Environment, BaseLoader
import app_resources

def render_template(template_res_path, data_json_path) -> str:
    # Get json
    data_collection = []
    with jsonlines.open(data_json_path) as reader:
            for obj in reader:
                data_collection.append(obj)
    # Create Jinja2 template
    template_str = app_resources.get_resource_content(template_res_path)
    template = Environment(loader=BaseLoader()).from_string(template_str)

    # Get current date in UTC
    current_date = datetime.datetime.now(datetime.UTC).strftime('%B %d, %Y')

    # Render the template
    output = template.render(articles=data_collection, current_date=current_date)

    return output