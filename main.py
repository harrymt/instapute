
import logging
import os
import webapp2
import jobmodel
import urllib2

from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.api import modules


from flask import Flask, render_template, request, redirect, url_for, jsonify


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')



def add_job_to_queue(job_id):
    task = taskqueue.add(url='/process-work/' + job_id, target="download-photos", params={'job_id': job_id})
    logging.info('Task {} enqueued, ETA {}.'.format(task.name, task.eta))



@app.route('/start_job', methods=["POST"])
def makeJob():
    username = request.form.get('username')

    new_job = createNewJobObject(username)

    job_id = new_job.put()

    add_job_to_queue(job_id.urlsafe())

    # ndb.Key(urlsafe=url_string).get() # Get back the job_id data
    return redirect('render/' + username + '/' + job_id.urlsafe())



def createNewJobObject(username):
    return jobmodel.Job(parent=ndb.Key('Job', username),
                username = username,
                is_completed = False,
                num_of_photos = 4, # Only works for 4
                final_image = None)



# Check if the render has been completed
@app.route('/render/<username>/<job_id>')
def render(username, job_id):

    # Load specified job
    job = ndb.Key(urlsafe=job_id).get()
    
    is_completed = False if job is None else job.is_completed
    msg = str(job)
    final_image = ''

    if is_completed:
        # Encode image to display it easily
        final_image = job.final_image.encode("base64")

        # Delete Kind from Cloud Datastore
        job.key.delete()
        pass

    return render_template('render.html', message=msg, completed=is_completed, job_id=job_id, username=username, final_image=final_image)



@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
