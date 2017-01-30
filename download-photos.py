
import logging
import os
import webapp2
import jobmodel
import urllib
import urllib2
import time
import json
import cloudstorage as gcs

from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.api import modules

from flask import Flask, render_template, request, redirect, url_for, jsonify

my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)



app = Flask(__name__)


@app.route('/process-work/<job_id>', methods=["POST", "GET"])
def process_work(job_id):
    logging.info("Processing job id {} in Task Queue...".format(job_id))

    thejob = ndb.Key(urlsafe=job_id).get()

    download_photos_from_user(job_id, thejob.username, thejob.num_of_photos)

    return "Processing work for job " + job_id + " completed"


def download_photos_from_user(job_id, username, num_of_photos):

    # download from this API
    api_url = "http://instagram.16bestof16.photos/api/getmedia/?userName=" + username
    logging.info("Downloading photos from instagram for user " + username)

    try:
        r = urllib2.urlopen(api_url)
    except urllib2.URLError:
        logging.exception('Caught exception fetching url')


    # Where we are going to save our files to
    bucket = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)

    data = json.load(r)
    photos = data['items']

    p_list = []
    # full_image_list = []
    # unique_id = 0
    firstTime = True
    for photo in photos:
        if firstTime == False and num_of_photos % 4 == 0:
            # Add the list of bucket filenames to a new taskqueue
            task = taskqueue.add(url='/build-image/' + job_id, target="build-image", params={'list': json.dumps(p_list), 'username': username})
            logging.info('Task build image {} enqueued, ETA {}.'.format(task.name, task.eta))

            # Clear the list
            # unique_id = unique_id + 1
            # full_image_list.append(unique_id)
            p_list = []

            if num_of_photos == 0:
                # # Finished processing now call API to stitch the image together
                # task2 = taskqueue.add(url='/finish-image/' + job_id + '/' + username, target="build-image", params={'list_unique_ids': json.dumps(full_image_list)})
                # logging.info('Task finish image {} enqueued, ETA {}.'.format(task2.name, task2.eta))
                break


        logging.info('Downloading photo to default bucket')
        photo_url = photo['images']['standard_resolution']['url']
        logging.info(photo_url)

        # Download photo to memory
        try:
            p = urllib2.urlopen(photo_url)
            content_type = p.headers['Content-Type']
        except urllib2.URLError:
            logging.exception('Caught exception fetching url')


        # Generate a unique filename for the photo
        filename = bucket + '/' + username + '-' + str(num_of_photos)

        # Append to a list
        p_list.append(filename)

        # Write photo to bucket
        gcs_file = gcs.open(filename,'w',content_type=content_type,retry_params=write_retry_params)
        gcs_file.write(p.read())
        p.close()
        gcs_file.close()
        logging.info("Sucessfully written a photo to bucket")


        num_of_photos = num_of_photos - 1
        firstTime = False

    return True


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
