from flask import Flask
app = Flask(__name__)


@app.route('/')
def root():
    return 'hello world!'


import vmock
import v100
