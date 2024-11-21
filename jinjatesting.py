from jinja2 import Environment, PackageLoader, select_autoescape

select_autoescape()
env = Environment(
    loader=PackageLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('index.html')
print(template.render())