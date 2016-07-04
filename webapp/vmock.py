VERSION_STR = 'vmock'


import util
import random
import requests
import numpy as np
from error import Error
from flask import Blueprint, request, jsonify

blueprint = Blueprint(VERSION_STR, __name__)


mock_eyes   = [util.read_file_in_base64('mocks/eye1.png'),
               util.read_file_in_base64('mocks/eye2.png'),
               util.read_file_in_base64('mocks/eye3.jpg')]

mock_faces  = [util.read_file_in_base64('mocks/face1.jpg'),
               util.read_file_in_base64('mocks/face2.jpg'),
               util.read_file_in_base64('mocks/face3.jpg')]

mock_photos = [util.read_file_in_base64('mocks/photo1.jpg'),
               util.read_file_in_base64('mocks/photo2.JPG'),
               util.read_file_in_base64('mocks/photo3.jpg')]


def gen_rand_Rect_object():
    rect = {'x': random.random() * 100.0,
            'y': random.random() * 100.0,
            'width': random.random() * 20.0,
            'height': random.random() * 20.0}
    return rect


def gen_rand_EyeInfo_object(annotate_image):
    eyeinfo = {}
    if annotate_image:
        eyeinfo['annotated_image'] = random.choice(mock_eyes)
    eyeinfo['leuko_prob'] = random.random()
    eyeinfo['process_time'] = random.random() * 2.0
    eyeinfo['rect'] = gen_rand_Rect_object()
    return eyeinfo


def gen_rand_FaceInfo_object(annotate_image):
    faceinfo = {}
    if annotate_image:
        faceinfo['annotated_image'] = random.choice(mock_faces)
    faceinfo['left_eye'] = gen_rand_EyeInfo_object(annotate_image)
    faceinfo['right_eye'] = gen_rand_EyeInfo_object(annotate_image)
    faceinfo['process_time'] = random.random() * 10.0
    faceinfo['rect'] = gen_rand_Rect_object()
    return faceinfo


def gen_rand_PhotoInfo_object(annotate_image):
    photoinfo = {}
    if annotate_image:
        photoinfo['annotated_image'] = random.choice(mock_photos)
    photoinfo['faces'] = [gen_rand_FaceInfo_object(annotate_image) \
                              for i in range(random.randint(0, 5))]
    return photoinfo


def obtain_encoded_image(request):
    '''
    All three routes below pass the image in the same way as one another.
    This function attempts to obtain the image, or it throws an error
    if the image cannot be obtained.
    '''

    if 'image_url' not in request.args:
        raise Error(387523, 'You must supply the `image_url` parameter')

    image_url = request.args['image_url']

    if image_url == 'body':
        encoded_image_str = request.data
    else:
        try:
            response = requests.get(image_url)
            encoded_image_str = response.content
        except:
            raise Error(2873, 'Invalid `image_url` parameter')

    return np.fromstring(encoded_image_str, dtype=np.uint8)


@blueprint.route('/process_eye')
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
      - vmock

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
        description: The URL of the image that should be processed, or the string 'body' if the image that should be processed is included in the body of this request (see `image_contents`)
        required: true
        type: string
      - name: image_contents
        in: body
        description: A binary dump of the image that should be processed. This is used when you need to upload an image for processing rather than specifying the URL of an existing image. If you want to upload an image for processing via the body of this request, you must pass the string 'body' to the parameter `image_url`.
        required: false
        schema:
          type: string
          format: binary
      - name: annotate_image
        in: query
        description: A boolean input flag (default=false) indicating whether or not to build and return annotated images within the `annotated_image` field of each response object
        required: false
        type: boolean

    consumes:
      - application/octet-stream

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


@blueprint.route('/process_face')
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
        description: The URL of the image that should be processed, or the string 'body' if the image that should be processed is included in the body of this request (see `image_contents`)
        required: true
        type: string
      - name: image_contents
        in: body
        description: A binary dump of the image that should be processed. This is used when you need to upload an image for processing rather than specifying the URL of an existing image. If you want to upload an image for processing via the body of this request, you must pass the string 'body' to the parameter `image_url`.
        required: false
        schema:
          type: string
          format: binary
      - name: annotate_image
        in: query
        description: A boolean input flag (default=false) indicating whether or not to build and return annotated images within the `annotated_image` field of each response object
        required: false
        type: boolean

    consumes:
      - application/octet-stream

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


@blueprint.route('/process_photo')
def process_photo():
    '''
    Find and process faces and eyes in a photo
    Find faces and eyes, and provide facial info of the given image.
    Note: If you use this endpoint to find faces, you do NOT need to use
    `process_face` or `process_eye` because this endpoint also processes
    the faces and eyes that are found.
    ---
    tags:
      - vmock

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
        description: The URL of the image that should be processed, or the string 'body' if the image that should be processed is included in the body of this request (see `image_contents`)
        required: true
        type: string
      - name: image_contents
        in: body
        description: A binary dump of the image that should be processed. This is used when you need to upload an image for processing rather than specifying the URL of an existing image. If you want to upload an image for processing via the body of this request, you must pass the string 'body' to the parameter `image_url`.
        required: false
        schema:
          type: string
          format: binary
      - name: annotate_image
        in: query
        description: A boolean input flag (default=false) indicating whether or not to build and return annotated images within the `annotated_image` field of each response object
        required: false
        type: boolean

    consumes:
      - application/octet-stream

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
