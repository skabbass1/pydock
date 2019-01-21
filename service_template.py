from jinja2 import Template

def generate_service_file(services):
    with open('service_template.ja2', 'r') as f:
        template = Template(f.read())
    return template.render(services=services)
