import time

from flask import Flask, jsonify, g, request, redirect
from flask_swagger import swagger

app = Flask(__name__)


APP_NAME = 'FaceInfo REST API'


@app.route('/')
def root():
    return redirect('./static/swagger-ui-build/index.html')


@app.route('/status')
def status():
    '''
    Get current status

    This endpoint provides a remote way to monitor this service
    and get status information about how well it is running.
    ---
    tags:
      - Miscellaneous

    parameters:
      - name: include_keys
        in: query
        description: A array of the keys that should be included in the response
        required: false
        type: array
      - name: exclude_keys
        in: query
        description: A array of keys that should be excluded from the response
        required: false
        type: array
      - name: request_interval
        in: query
        description: The number of recent requests to include when calculating 'avg_response_time' (default=100)
        required: false
        type: integer
      - name: time_interval
        in: query
        description: The number of seconds of recent activity to include when calculating 'num_requests' (default=60)
        required: false
        type: integer

    responses:
      200:
        description: A status info object
        schema:
          $ref: '#/definitions/StatusInfo'
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    definitions:
      - schema:
          id: StatusInfo
          type: object
          required:
            - service_name
          properties:
            uptime:
              type: integer
              description: the number of seconds this service has been running
            num_requests:
              type: integer
              description: the number of requests this service has received in the last 'time_interval' number of seconds
            avg_response_time:
              type: number
              description: the average time in milliseconds that it took to generate the last 'request_interval' responses
            service_name:
              type: string
              description: the name of this service
      - schema:
          id: Error
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: integer
            message:
              type: string
              description: the human readable description of this error's error code
    '''
    # TODO: actually provide real functions that do real stuff...
    info = {'avg_response_time': lambda: -1.0,
            'num_requests': lambda: -1,
            'service_name': lambda: APP_NAME,
            'uptime': lambda: -1
           }
    include_keys = request.args.get('include_keys', info.keys())
    exclude_keys = request.args.get('exclude_keys', [])
    request_interval = request.args.get('request_interval', 100)
    time_interval = request.args.get('time_interval', 60)
    keys = (set(info.keys()) & set(include_keys)) - set(exclude_keys)
    res = {k: info[k]() for k in keys}
    return jsonify(res)


@app.before_request
def before_request():
    g.start_time = time.time()


@app.after_request
def after_request(response):
    diff = time.time() - g.start_time
    diff *= 1000.0  # to convert from seconds to milliseconds
    info = '%.4f ms <-- %s' % (diff, request.path)
    app.logger.info(info)
    return response


@app.route('/spec')
def spec():
    swag = swagger(app)
    swag['info']['version'] = "multiple"
    swag['info']['title'] = APP_NAME
    return jsonify(swag)


import vmock
import v100
