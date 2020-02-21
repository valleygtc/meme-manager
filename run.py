import os

from waitress import serve

from manage import app


port = os.getenv('PORT', 5000)
serve(app, listen=f'*:{port}')
