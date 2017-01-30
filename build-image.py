
import logging
import os
import webapp2
import jobmodel
import urllib
import urllib2
import time
import json
import cloudstorage as gcs
import ast


from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.api import modules
from google.appengine.api import images
from google.appengine.api import blobstore

from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)



@app.route('/build-image/<job_id>', methods=["POST", "GET"])
def process_work(job_id):
    logging.info("Building image job id {} in Task Queue...".format(job_id))

    bucket = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)

    # Get params to see the image bucket urls
    photo_list_payload = request.form.get('list')
    unique_id = request.form.get('unique_id')
    username = request.form.get('username')

    photo_list = ast.literal_eval(photo_list_payload)

    list_of_actual_photos = []

    job = ndb.Key(urlsafe=job_id).get()

    base_size = 640 # work_out_base_size(job.num_of_photos)
    target_size = base_size / 2

    for photo_filename in photo_list:

        # Read file from bucket
        gcs_file = gcs.open(photo_filename)
        image_bytes = gcs_file.read()

        # Resize to a 1/2 of current size!
        resized_img = images.resize(image_bytes, target_size, target_size)

        # Add to list
        list_of_actual_photos.append(resized_img)
        gcs_file.close()

        # Delete file from bucket
        gcs.delete(photo_filename)


    # Combine the photos
    combined_image = images.composite([
        (list_of_actual_photos[0], 0, 0, 1.0, images.TOP_LEFT), (list_of_actual_photos[1], target_size, 0, 1.0, images.TOP_LEFT),
        (list_of_actual_photos[2], 0, target_size, 1.0, images.TOP_LEFT), (list_of_actual_photos[3], target_size, target_size, 1.0, images.TOP_LEFT)
        ]
        , base_size, base_size)


    # Mark job as finished
    job = ndb.Key(urlsafe=job_id).get()
    job.final_image = combined_image
    job.is_completed = True
    job.put()
    
    # # Save image in bucket
    # # Generate a unique filename for the combined photo
    # filename = bucket + '/' + username + '-' + str(unique_id)

    # # Write photo to bucket
    # gcs_file = gcs.open(filename,'w',content_type='image/jpg',retry_params=write_retry_params)
    # gcs_file.write(combined_image)
    # gcs_file.close()
    # logging.info("Sucessfully written a photo to bucket")

    return "Building image for job " + job_id + " completed"


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)



# For 4+ photos

# # TODO turn this into an algo
# def work_out_base_size(number_of_photos):
#     if number_of_photos == 4:
#         return 640
    
#     if number_of_photos == 16:
#         return 320

#     return 640


# @app.route('/finish-image/<job_id>/<username>', methods=["POST", "GET"])
# def stitch_image_together(job_id, username):
#     logging.info("Stitching image together! {} ".format(job_id))

#     bucket = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
#     write_retry_params = gcs.RetryParams(backoff_factor=1.1)

#     photo_list_payload = request.form.get('list_unique_ids')
#     photo_list = ast.literal_eval(photo_list_payload)

#     the_final_images = []

#     base_size = 640
#     target_size = base_size / 2

#     for photo_unique_id in photo_list:
#         print photo_unique_id
#         photo_filename = bucket + '/' + username + '-' + str(photo_unique_id)
#         gcs_file = gcs.open(photo_filename)
#         image_bytes = gcs_file.read()
#         the_final_images.append(image_bytes)
#         gcs_file.close()


#     if len(photo_list) > 1:
#         # Combine the images
#         combined_image = images.composite([
#             (the_final_images[0], 0, 0, 1.0, images.TOP_LEFT), (the_final_images[1], target_size, 0, 1.0, images.TOP_LEFT),
#             (the_final_images[2], 0, target_size, 1.0, images.TOP_LEFT), (the_final_images[3], target_size, target_size, 1.0, images.TOP_LEFT)
#             ]
#             , base_size, base_size)
#     else:
#         combined_image = the_final_images[0]

#     # Save image in final image in job based on job_id
#     job = ndb.Key(urlsafe=job_id).get()
#     job.final_image = combined_image
#     job.is_completed = True
#     job.put()
#     return "Finished job"

