import boto3
import uuid

from flask import Flask, jsonify, request, make_response, redirect, url_for, render_template

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        uploaded_file = request.files["file-to-upload"]
        if not allowed_file(uploaded_file.filename):
            return "FILE NOT ALLOWED!"

        new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()

        bucket_name = "number-plates-detection-demo-prod"
        s3 = boto3.resource("s3")
        s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)

        # file = File(original_filename=uploaded_file.filename, filename=new_filename,
        #     bucket=bucket_name, region="us-east-2")

        # db.session.add(file)
        # db.session.commit()

        return redirect(url_for("index"))
    return render_template('index.html')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
