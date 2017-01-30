## Instapute

A photo manipulation application named Instapute, hosted on Google App Engine. The application can perform various image manipulation tasks on a large number of images. The use case design demonstrates these tasks by resizing 4 images and composites them together to create a single image. This application can be run online at https://front-end-dot-ccinstapute.appspot.com

### Overview

Written in Python, using GAE, Instapute uses the following technology:

- [Flask](flask.pocoo.org) a Python micro framework
- [WebApp2](https://webapp2.readthedocs.io/en/latest/) a Python web framework for easy routing with GAE
- The following Google App Engine APIs
  - [App Identity](https://cloud.google.com/appengine/docs/python/appidentity/) to get the name of a bucket to store photos in
  - [Push Task Queues](https://cloud.google.com/appengine/docs/python/taskqueue/push/) to queue up tasks, such as a new job to create a collage for a particular instagram user, or resize 4 images to a single image.
  - [Services](https://cloud.google.com/appengine/docs/python/microservices-on-app-engine) (previously named modules), to separate the program into several microservices ... 'Microservices allow a large application to be decomposed into independent constituent parts, with each part having its own realm of responsibility.' ... Cloud Computing benifits, such as autoscaling, load balancing, and machine instance types are all managed independently for services.
- The following Google App Engine Storage systems
  - [Google Cloud Datastore](https://cloud.google.com/appengine/docs/python/ndb/entity-property-reference) to store data types for property values.
  - [Google Cloud Storage](https://cloud.google.com/appengine/docs/python/googlecloudstorageclient/read-write-to-cloud-storage) a bucket to store and serve files, such as images or other static content.

The program is setup with the following structure:

```
- templates/
    directory contains all html templates
- static/
    directory contains all static files, such as .css files or .js files
- Imaging-1.1.7/
    directory contains PIL Imaging library so the GAE development server can process image functions (needed?)
- requests/
    directory contains requests library so the GAE dev server can process requests api functions (needed?)
- appengine_config.py
    to use the above libraries
- makefile
    to make the flask project (needed?)
- jobmodel.py
    defines a GAE Google Cloud Datastore for an Entity
- requirements.txt
    defines all libraries required
- The following 3 micro-services
  - front-end
      defined in main.py with app.yaml
  - download-photos
      defined in download-photos.py with download-photos.yaml
  - build-image
      defined in build-image.py with build-image.yaml
```

### Initial Setup

1. Setup a Google Cloud project
  gcloud init
2. Set the project to be the name (ccinstapute)
  gcloud source repos clone default --project=ccinstapute
3. Pull and deploy (see SETUP below)

#### Local

1. Install Python 2.7 and PIP
2. Pull repo
3. Install all requirements into a folder in the directory instapute/lib/
4. Run the makefile to test locally
  - cd /instapute
  - make
  - http://localhost:5000/
5. Commit to repo, could use a shorthand to commit with no message
  - git add . && git commit -am. && git push

#### Remote

1. When commited to Github Repo, go to cloud console
  - https://console.cloud.google.com/
2. Type the following to pull
  - cd src/default
  - git pull
3. Test locally by running
  - git pull && dev_appserver.py app.yaml download-photos.yaml build-image.yaml
  - Click preview in browser button
4. Deploy by running
  - gcloud app deploy app.yaml download-photos.yaml build-image.yaml
  - Y
5. View app at location
    https://front-end-dot-ccinstapute.appspot.com


### Uses Instagram API from 16bestof16

Instagram API call
```
http://instagram.16bestof16.photos/api/getmedia/?userName=<username>
```

Navigates the JSON to get photos with a python call like:

```python
for each photos
  item[x]['images']['standard_resolution']['url']
```

### Example JSON response from API

```json
{
   "status":"ok",
   "items":[
      {
         "can_delete_comments":false,
         "code":"BJsSTn8hi__",
         "location":{
            "name":"Location Name"
         },
         "images":{
            "low_resolution":{
               "url":"https://scontent.cdninstagram.com/t51.2885-15/s320x320/e35/141346123123234_1205982709_n.jpg?ig_cache_key=MTMyNzUxNjUwMzasde2OTc1OQ%3D%3D.2",
               "width":320,
               "height":320
            },
            "thumbnail":{
               "url":"https://scontent.cdninstagram.com/t51.2885-15/s150x150/e35/14134617_32171asdasd4_1205982709_n.jpg?ig_cache_key=MTMyNzUxasda2OTc1OQ%3D%3D.2",
               "width":150,
               "height":150
            },
            "standard_resolution":{
               "url":"https://scontent.cdninstagram.com/t51.2885-15/s640x640/sh0.08/e35/14134617_12e12asda3784_1205982709_n.jpg?ig_cache_key=MTMyNzUasdU2NjA2OTc1OQ%3D%3D.2",
               "width":640,
               "height":640
            }
         },
         "can_view_comments":true,
         "comments":{
            "count":0,
            "data":[

            ]
         },
         "alt_media_url":null,
         "caption":{
            "created_time":"147ae22320",
            "text":"🐱",
            "from":{
               "username":"<username>",
               "profile_picture":"https://scontent.cdninstagram.com/t51.2885-19/s150x150/14727572_32592aasdasd446214874398720_a.jpg",
               "id":"674465",
               "full_name":"John"
            },
            "id":"d1dw"
         },
         "link":"https://www.instagram.com/p/asdasd1w1d/",
         "likes":{
            "count":18,
            "data":[
               {
                  "username":"asdasd",
                  "profile_picture":"https://scontent.cdninstagram.com/t51.2885-19/asdasd.jpg",
                  "id":"asdasd",
                  "full_name":"asdas"
               }
            ]
         },
         "created_time":"1472472320",
         "type":"image",
         "id":"asdasd",
         "user":{
            "username":"_mumf",
            "profile_picture":"https://scontent.cdninstagram.com/t51.2885-19/s150x150/asdasdasd.jpg",
            "id":"asdas",
            "full_name":"asdas"
         }
      }
   ],
   "more_available":true
}
```
