import json
import datetime
import json
from jinja2 import Environment, BaseLoader
from media_agents.app_resources import get_resource_content

def render_template(template_res_path, data_json_path) -> str:
    # Get json
    data_collection = []
    with open(data_json_path, 'r') as fr:
        for line in fr.readlines():
            data_collection.append(json.loads(line))
    for item in data_collection:
        keys = list(item.keys())
        for k in keys:
            if 'date' in k:
                try:
                    item[k] = datetime.datetime.fromisoformat(item[k]).strftime('%B %d, %Y')
                except Exception:
                    continue

    # Create Jinja2 template
    template_str = get_resource_content(template_res_path)
    template = Environment(loader=BaseLoader()).from_string(template_str)

    # Get current date in UTC
    current_date = datetime.datetime.now(datetime.UTC).strftime('%B %d, %Y')

    # Render the template
    output = template.render(articles=data_collection, current_date=current_date)

    return output