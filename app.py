import boto3
import uuid
import os
import logging
import re

from botocore.exceptions import ClientError
from flask import Flask, request, render_template

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        uploaded_file = request.files['file-to-upload']
        if not allowed_file(uploaded_file.filename):
            return 'FILE NOT ALLOWED!'

        new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()

        bucket_name = os.environ['BUCKET']
        s3 = boto3.resource('s3')

        s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)
        s3_client = boto3.client('s3')
        try:
            response_filepath = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name,
                                                                'Key': new_filename},
                                                        ExpiresIn=3600)
        except ClientError as e:
            logging.error(e)
            return None

        rekognition = boto3.client('rekognition')
        response = rekognition.detect_labels(
            Image = {
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': new_filename
                }
            }, MaxLabels=1000, MinConfidence=0
        )

        plate_detected = False
        license_plate_list = []
        for idx,item in enumerate(response['Labels']):
            if item["Name"] == "License Plate":
                plate_detected = True
                if len(item['Instances']) != 0:
                    for i in item['Instances']:
                        license_plate_list.append([i['BoundingBox']['Width'],i['BoundingBox']['Height'],i['BoundingBox']['Left'],i['BoundingBox']['Top']])

        for idx,item in enumerate(license_plate_list):
            license_plate_loc = item
            # OCR for number plate on filtered image location.
            PlateNumber = rekognition.detect_text(
                Image={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': new_filename
                    }
                },
                Filters={
                    'RegionsOfInterest': [
                        {
                            'BoundingBox': {
                                'Width': license_plate_loc[0],
                                'Height': license_plate_loc[1],
                                'Left': license_plate_loc[2],
                                'Top': license_plate_loc[3]
                            },
                        },
                    ]
                })
            classification_number, plate_number = '', ''
            for elem in PlateNumber['TextDetections']:
                #confidence_score = elem['Confidence']
                elem = elem['DetectedText']
                # 3桁の分類番号
                matches = re.findall(r"\d{3}", elem)
                if matches != []:
                    classification_number = matches[0]
                # ハイフンで区切られた4桁のナンバー
                matches = re.findall(r"\d{2}-\d{2}", elem)
                if matches != []:
                    plate_number = matches[0]

        return render_template('index.html', filepath=response_filepath, classification_number = classification_number, plate_number=plate_number)
    return render_template('index.html')
