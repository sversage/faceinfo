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
    Use `find_faces` to locate and process faces within an image.
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
      - name: annotate_image
        in: query
        description: A boolean input flag (default=false) indicating whether or not to build and return annotated images within the `annotated_image` field of each response object
        required: false
        type: boolean

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
            annotated_image:
              type: string
              format: byte
              description: base64 encoded annotated image of this face
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
            annotated_image:
              type: string
              format: byte
              description: base64 encoded annotated image of this eye
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
    Note: If you use this endpoint to find faces, you do NOT need to use
    `process_face` because this endpoint also processes the faces that
    are found.
    ---
    tags:
      - vmock

    responses:
      200:
        description: An image info objects
        schema:
          $ref: '#/definitions/ImageInfo'
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
      - name: annotate_image
        in: query
        description: A boolean input flag (default=false) indicating whether or not to build and return annotated images within the `annotated_image` field of each response object
        required: false
        type: boolean

    definitions:
      - schema:
          id: ImageInfo
          type: object
          required:
            - faces
          properties:
            faces:
              description: an array of FaceInfo objects found in this image
              schema:
                type: array
                items:
                  $ref: '#/definitions/FaceInfo'
            annotated_image:
              type: string
              format: byte
              description: base64 encoded annotated image
    '''
    return VERSION_STR


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
