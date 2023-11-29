import boto3
import uuid
import os

from flask import Flask, request, redirect, url_for, render_template

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
        region = os.environ['REGION']
        s3 = boto3.resource('s3')
        s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)

        filepath = "https://" + bucket_name + ".s3." + region + ".amazonaws.com/" + new_filename
        return render_template('index.html', filepath=filepath)
    return render_template('index.html')
