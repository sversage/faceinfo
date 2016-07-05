VERSION_STR = 'v1.0.0'


import cv2
import base64
import requests
import numpy as np
from error import Error
from flask import Blueprint, request, jsonify

blueprint = Blueprint(VERSION_STR, __name__)


FACE_CASCADE = cv2.CascadeClassifier("resources/cascades/haarcascades/haarcascade_frontalface_alt.xml")
EYE_CASCADE = cv2.CascadeClassifier("resources/cascades/haarcascades/haarcascade_eye.xml")


def base64_encode_image(image_rgb):
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    ret, image_buf = cv2.imencode('.jpg', image_bgr, (cv2.IMWRITE_JPEG_QUALITY, 40))
    image_str = base64.b64encode(image_buf)
    return 'data:image/jpeg;base64,' + image_str


def eye_regions(face_rect):
    side_inset = 0.1
    top_inset = 0.2
    bottom_inset = 0.35
    x, y, width, height = face_rect

    left_eye_rect  = (x + width*side_inset,
                      y + height*top_inset,
                      width*(0.5-side_inset),
                      height*(1-top_inset-bottom_inset))
    right_eye_rect = (x + 0.5*width,
                      y + height*top_inset,
                      width*(0.5-side_inset),
                      height*(1-top_inset-bottom_inset))

    eye_rects = [left_eye_rect, right_eye_rect]
    return [tuple([int(round(v)) for v in rect]) for rect in eye_rects]


def build_Rect(x, y, w, h):
    return {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}


def build_EyeInfo(x_offset, y_offset, eye_image_gray, annotated_rgb):
    eyeinfo = {}

    eyeinfo['rect'] = build_Rect(x_offset, y_offset,
                                 eye_image_gray.shape[1],
                                 eye_image_gray.shape[0])

    eyeinfo['leuko_prob'] = 0.0             # TODO

    if annotated_rgb != None:
        eyeinfo['annotated_image'] = base64_encode_image(annotated_rgb)

    eyeinfo['process_time'] = 0.0           # TODO

    return eyeinfo


def build_FaceInfo(x_offset, y_offset, face_image_gray, annotated_rgb):
    faceinfo = {}

    w = face_image_gray.shape[1]
    h = face_image_gray.shape[0]

    faceinfo['rect'] = build_Rect(x_offset, y_offset, w, h)

    regions = eye_regions((0, 0, w, h))
    keys = ['left_eye', 'right_eye']

    eye_color = [0, 255, 0]
    thickness = 4

    for region, key in zip(regions, keys):

        x_roi, y_roi, w_roi, h_roi = region

        eye_image_roi_gray = face_image_gray[y_roi : y_roi + h_roi,
                                             x_roi : x_roi + w_roi]

        eyes = EYE_CASCADE.detectMultiScale(eye_image_roi_gray,
                                            scaleFactor=1.05,
                                            minNeighbors=3,
                                            minSize=(15, 15),
                                            flags = cv2.CASCADE_SCALE_IMAGE)

        if len(eyes) == 0:
            faceinfo[key] = None
            continue

        x_eye, y_eye, w_eye, h_eye = eyes[0]

        sub_annotated_rgb = None
        if annotated_rgb != None:
            cv2.rectangle(annotated_rgb,
                          (x_roi + x_eye,         y_roi + y_eye),
                          (x_roi + x_eye + w_eye, y_roi + y_eye + h_eye),
                          eye_color, thickness)
            sub_annotated_rgb = annotated_rgb[y_roi + y_eye : y_roi + y_eye + h_eye,
                                              x_roi + x_eye : x_roi + x_eye + w_eye]

        eye_image_gray = face_image_gray[y_roi + y_eye : y_roi + y_eye + h_eye,
                                         x_roi + x_eye : x_roi + x_eye + w_eye]

        faceinfo[key] = build_EyeInfo(x_roi + x_eye, y_roi + y_eye, eye_image_gray, sub_annotated_rgb)

    if annotated_rgb != None:
        faceinfo['annotated_image'] = base64_encode_image(annotated_rgb)

    faceinfo['process_time'] = 0.0    # TODO

    return faceinfo


def build_PhotoInfo(image_gray, annotated_rgb):

    photoinfo = {}

    faces = FACE_CASCADE.detectMultiScale(image_gray,
                                          scaleFactor=1.1,
                                          minNeighbors=3,
                                          minSize=(45, 45),
                                          flags = cv2.CASCADE_SCALE_IMAGE)

    face_color = [0, 0, 255]
    thickness = 4

    face_objects = []

    for x_face, y_face, w_face, h_face in faces:

        face_image_gray = image_gray[y_face : y_face + h_face,
                                     x_face : x_face + w_face]

        sub_annotated_rgb = None
        if annotated_rgb != None:
            cv2.rectangle(annotated_rgb,
                          (x_face,          y_face),
                          (x_face + w_face, y_face + h_face),
                          face_color, thickness)
            sub_annotated_rgb = annotated_rgb[y_face : y_face + h_face,
                                              x_face : x_face + w_face]

        face_objects.append(build_FaceInfo(x_face, y_face, face_image_gray, sub_annotated_rgb))

    photoinfo['faces'] = face_objects

    if annotated_rgb != None:
        photoinfo['annotated_image'] = base64_encode_image(annotated_rgb)

    return photoinfo


def obtain_images(request):
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

    encoded_image_buf = np.fromstring(encoded_image_str, dtype=np.uint8)
    decoded_image_bgr = cv2.imdecode(encoded_image_buf, cv2.IMREAD_COLOR)

    image_rgb = cv2.cvtColor(decoded_image_bgr, cv2.COLOR_BGR2RGB)
    image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    annotate_image = (request.args.get('annotate_image', 'false').lower() == 'true')
    if annotate_image:
        annotated_rgb = np.copy(image_rgb)
    else:
        annotated_rgb = None
    return image_rgb, image_gray, annotated_rgb


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
    image_rgb, image_gray, annotated_rgb = obtain_images(request)
    eyeinfo = build_EyeInfo(0, 0, image_gray, annotated_rgb)
    return jsonify(eyeinfo)


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
    image_rgb, image_gray, annotated_rgb = obtain_images(request)
    faceinfo = build_FaceInfo(0, 0, image_gray, annotated_rgb)
    return jsonify(faceinfo)


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
    image_rgb, image_gray, annotated_rgb = obtain_images(request)
    photoinfo = build_PhotoInfo(image_gray, annotated_rgb)
    return jsonify(photoinfo)


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
