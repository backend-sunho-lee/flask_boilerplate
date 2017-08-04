# -*- coding: utf-8 -*-
from app import app
from gevent.wsgi import WSGIServer

#: HTTPS, SSL 설정
# cert = './cert_key/mysite.cert.pem'
# key = './cert_key/mysite.key.pem'

#: Method 1. 스레드 하나만 돌릴 때
http = WSGIServer(('0.0.0.0', 5000), app)
http.serve_forever()
# https = WSGIServer(('0.0.0.0', 5000), app, keyfile=key, certfile=cert)
# https.serve_forever()

#: Method 2. 멀티스레드일 때
# THREADS_PER_PAGE 설정을 1로하면 멀티가 아니지 않을까?..
# app.run()
# context = (cert, key)
# app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)
