import boto3
import uuid
import os
import logging

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
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name,
                                                                'Key': new_filename},
                                                        ExpiresIn=3600)
        except ClientError as e:
            logging.error(e)
            return None

        return render_template('index.html', filepath=response)
    return render_template('index.html')
