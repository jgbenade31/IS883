# This file is forked from the google codelab example available at
# https://github.com/GoogleCloudPlatform/python-docs-samples.git


from datetime import datetime
import logging
import os

from flask import Flask, redirect, render_template, request

from google.cloud import datastore
from google.cloud import storage
from google.cloud import vision


CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')


app = Flask(__name__)


@app.route('/')
def homepage():
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    query = datastore_client.query(kind='Labelled-images')

    ## TODO 2.3 - sort the results by timestamp (most recent first)
    #
    # your code here (remove the comments)
    #
    ## YOUR CODE ENDS HERE ####

    image_entities = list(query.fetch())

    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    return render_template('homepage.html', image_entities=image_entities)


@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    photo = request.files['file']

    # Create a Cloud Storage client.
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(photo.filename)
    blob.upload_from_string(
            photo.read(), content_type=photo.content_type)

    # Make the blob publicly viewable.
    blob.make_public()

    # Create a Cloud Vision client.
    vision_client = vision.ImageAnnotatorClient()

    # Use the Cloud Vision client to detect a face for our image.
    source_uri = 'gs://{}/{}'.format(CLOUD_STORAGE_BUCKET, blob.name)
    image = vision.types.Image(
        source=vision.types.ImageSource(gcs_image_uri=source_uri))
    
    #### do labelling
    # variables used to store labels and probablilities of 2 most likely labels
    first_label, second_label = "", ""
    first_probability, second_probability = -1, -1

    ## TODO 2.1 - Call vision api for labelling
    #
    # your code here (remove the comments)
    #
    ## YOUR CODE ENDS HERE ####

    #### safe search
    # variable used to store safe search status
    is_unsafe = 'UNKNOWN'
    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                        'LIKELY', 'VERY_LIKELY')

    ## TODO 2.2 - Call safe search api 
    #
    # your code here (remove the comments)
    #
    ## YOUR CODE ENDS HERE ####

    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch the current date / time.
    current_datetime = datetime.now()

    # The kind for the new entity.
    kind = 'Labelled-images'

    # The name/ID for the new entity.
    name = blob.name

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key(kind, name)

    # Construct the new entity using the key. Set dictionary values for entity
    # keys blob_name, storage_public_url, timestamp, and joy.
    entity = datastore.Entity(key)
    entity['blob_name'] = blob.name
    entity['image_public_url'] = blob.public_url
    entity['timestamp'] = current_datetime
    entity['label1'] = first_label
    entity['label2'] = second_label
    entity['prob1'] = first_probability
    entity['prob2'] = second_probability
    entity['unsafe'] = is_unsafe

    # Save the new entity to Datastore.
    datastore_client.put(entity)

    # Redirect to the home page.
    return redirect('/')


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
