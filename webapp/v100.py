VERSION_STR = 'v1.0.0'


import requests
import numpy as np
from error import Error
from flask import Blueprint, request, jsonify

blueprint = Blueprint(VERSION_STR, __name__)


def obtain_encoded_image(request):
    '''
    All three routes below pass the image in the same way as one another.
    This function attempts to obtain the image, or it throws an error
    if the image cannot be obtained.
    '''

    if 'image_url' in request.args:
        image_url = request.args['image_url']
        try:
            response = requests.get(image_url)
            encoded_image_str = response.content
        except:
            raise Error(2873, 'Invalid `image_url` parameter')

    elif 'image_buf' in request.files:
        image_buf = request.files['image_buf']  # <-- FileStorage object
        encoded_image_str = image_buf.read()

    else:
        raise Error(35842, 'You must supply either `image_url` or `image_buf`')

    if encoded_image_str == '':
        raise Error(5724, 'You must supply a non-empty input image')

    return np.fromstring(encoded_image_str, dtype=np.uint8)


@blueprint.route('/process_eye', methods=['POST'])
def process_eye():
    '''
    Process one eye
    Process a cropped image of an eye and return info about the eye.
    Note: This endpoint does NOT find faces or eyes in the image. Rather, it
    assumes the given image contains exactly one pre-cropped eye.
    Alternatively, use `process_photo` to locate and process faces and eyes
    within an image.
    ---
    tags:
      - v1.0.0

    responses:
      200:
        description: An eye info object
        schema:
          $ref: '#/definitions/EyeInfo'
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: image_url
        in: query
        description: The URL of an image that should be processed. If this field is not specified, you must pass an image via the `image_buf` form parameter.
        required: false
        type: string
      - name: image_buf
        in: formData
        description: An image that should be processed. This is used when you need to upload an image for processing rather than specifying the URL of an existing image. If this field is not specified, you must pass an image URL via the `image_url` parameter.
        required: false
        type: file
      - name: annotate_image
        in: query
        description: A boolean input flag (default=false) indicating whether or not to build and return annotated images within the `annotated_image` field of each response object
        required: false
        type: boolean

    consumes:
      - multipart/form-data
      - application/x-www-form-urlencoded

    definitions:
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
    encoded_image = obtain_encoded_image(request)
    annotate_image = (request.args.get('annotate_image', 'false').lower() == 'true')
    return jsonify(gen_rand_EyeInfo_object(annotate_image))


@blueprint.route('/process_face', methods=['POST'])
def process_face():
    '''
    Process one face
    Process a cropped image of a face and return info about the face.
    Note: This endpoint does NOT find faces in the image. Rather, it
    assumes the given image contains exactly one pre-cropped face.
    This endpoint also finds and processes eyes, so you do NOT need to call
    `process_eye` when using this endpoint. Alternatively, use `process_photo`
    to locate and process faces within an image.
    ---
    tags:
      - v1.0.0

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
        description: The URL of an image that should be processed. If this field is not specified, you must pass an image via the `image_buf` form parameter.
        required: false
        type: string
      - name: image_buf
        in: formData
        description: An image that should be processed. This is used when you need to upload an image for processing rather than specifying the URL of an existing image. If this field is not specified, you must pass an image URL via the `image_url` parameter.
        required: false
        type: file
      - name: annotate_image
        in: query
        description: A boolean input flag (default=false) indicating whether or not to build and return annotated images within the `annotated_image` field of each response object
        required: false
        type: boolean

    consumes:
      - multipart/form-data
      - application/x-www-form-urlencoded

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
    '''
    encoded_image = obtain_encoded_image(request)
    annotate_image = (request.args.get('annotate_image', 'false').lower() == 'true')
    return jsonify(gen_rand_FaceInfo_object(annotate_image))


@blueprint.route('/process_photo', methods=['POST'])
def process_photo():
    '''
    Find and process faces and eyes in a photo
    Find faces and eyes, and provide facial info of the given image.
    Note: If you use this endpoint to find faces, you do NOT need to use
    `process_face` or `process_eye` because this endpoint also processes
    the faces and eyes that are found.
    ---
    tags:
      - v1.0.0

    responses:
      200:
        description: A photo info objects
        schema:
          $ref: '#/definitions/PhotoInfo'
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: image_url
        in: query
        description: The URL of an image that should be processed. If this field is not specified, you must pass an image via the `image_buf` form parameter.
        required: false
        type: string
      - name: image_buf
        in: formData
        description: An image that should be processed. This is used when you need to upload an image for processing rather than specifying the URL of an existing image. If this field is not specified, you must pass an image URL via the `image_url` parameter.
        required: false
        type: file
      - name: annotate_image
        in: query
        description: A boolean input flag (default=false) indicating whether or not to build and return annotated images within the `annotated_image` field of each response object
        required: false
        type: boolean

    consumes:
      - multipart/form-data
      - application/x-www-form-urlencoded

    definitions:
      - schema:
          id: PhotoInfo
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
    encoded_image = obtain_encoded_image(request)
    annotate_image = (request.args.get('annotate_image', 'false').lower() == 'true')
    return jsonify(gen_rand_PhotoInfo_object(annotate_image))


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
