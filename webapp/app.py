from flask import Flask, jsonify
from flask_swagger import swagger

app = Flask(__name__)


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
              type: number
              format: integer
              description: the number of seconds this service has been running
            num_requests:
              type: number
              format: integer
              description: the number of requests this service has received
            avg_response_time:
              type: number
              format: double
              description: the average time in microseconds that it takes to generate a response
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
              type: number
              format: integer
            message:
              type: string
              description: the human readable description of this error's error code
    '''
    return 'hello world!'


@app.route('/spec')
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0.0"
    swag['info']['title'] = "FaceInfo REST API"
    return jsonify(swag)


import vmock
import v100
