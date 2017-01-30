from google.appengine.ext import ndb

class Job(ndb.Model):
    """Model for representing a job in the DB."""
    job_id = ndb.IntegerProperty() # TODO delete this????
    is_completed = ndb.BooleanProperty()
    username = ndb.StringProperty()
    num_of_photos = ndb.IntegerProperty() # multiples of 8, 16
    final_image = ndb.BlobProperty()
