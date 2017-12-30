from flask import Flask, request


app = Flask(__name__)

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/', methods=['GET'])
def router():
    return handlers(request.args)


def handlers(args):
    pass
