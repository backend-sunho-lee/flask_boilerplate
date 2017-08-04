from app import app, versions
import app.module02.controllers as module02

for ver in versions:
    app.add_url_rule('{}/about'.format(ver), view_func=module02.hello, methods=['GET'])
    app.add_url_rule('{}/colors/<palette>/'.format(ver), view_func=module02.colors)