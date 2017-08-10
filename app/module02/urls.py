from app import app, versions
import app.module02.controllers as module02

for ver in versions:
    app.add_url_rule('{}/module02/'.format(ver), view_func=module02.index, methods=['GET'])
    app.add_url_rule('{}/modules02/language/<string:language>'.format(ver), view_func=module02.language_awesomeness, methods=['GET'])
