VERSION_STR = 'vmock'


from error import Error
from flask import Blueprint

blueprint = Blueprint(VERSION_STR, __name__)


@blueprint.route('/process_face')
def process_face():
    '''
    Process one face
    Process a cropped image of a face and return info about the face.
    Note: This endpoint does NOT find faces in the image. Rather, it
    assumes the given image contains exactly one pre-cropped face.
    ---
    tags:
      - vmock

    responses:
      200:
        description: A face info object
        schema:
          $ref: '#/definitions/FaceInfo'
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: image_url
        in: query
        description: The URL to the image that should be processed
        required: true
        type: string

    definitions:
      - schema:
          id: FaceInfo
          type: object
          required:
            - rect
            - left_eye
            - right_eye
            - process_time
          properties:
            rect:
              description: This face's rectangle within the image
              schema:
                $ref: '#/definitions/Rect'
            left_eye:
              description: Info about the left eye
              schema:
                $ref: '#/definitions/EyeInfo'
            right_eye:
              description: Info about the right eye
              schema:
                $ref: '#/definitions/EyeInfo'
            process_time:
              type: number
              description: the processing time in milliseconds taken to build this object
      - schema:
          id: EyeInfo
          type: object
          required:
            - rect
            - leuko_prob
            - process_time
          properties:
            rect:
              description: This eye's rectangle within the image
              schema:
                $ref: '#/definitions/Rect'
            leuko_prob:
              type: number
              description: The probability of leukocoria in this eye (in [0, 1])
            process_time:
              type: number
              description: the processing time in milliseconds taken to build this object
      - schema:
          id: Rect
          type: object
          required:
            - x
            - y
            - width
            - height
          properties:
            x:
              type: number
            y:
              type: number
            width:
              type: number
            height:
              type: number
    '''
    return VERSION_STR


@blueprint.route('/find_faces')
def find_faces():
    '''
    Find and process faces in an image
    Find faces and provide facial info of the given image.
    ---
    tags:
      - vmock

    responses:
      200:
        description: An array of face info objects
        schema:
          $ref: '#/definitions/FaceInfoArray'
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: image_url
        in: query
        description: The URL to the image that should be processed
        required: true
        type: string

    definitions:
      - schema:
          id: FaceInfoArray
          type: array
          items:
            $ref: '#/definitions/FaceInfo'
    '''
    return VERSION_STR


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
