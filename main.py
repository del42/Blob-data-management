#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import urllib
import webapp2
import cgi

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Customer(db.Model):
    email = db.StringProperty()
    image_key = db.StringProperty()
    image = blobstore.BlobReferenceProperty()
    type = db.StringProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        datas = db.GqlQuery("SELECT * FROM Customer")
        upload_url = blobstore.create_upload_url('/upload')        
        template_values = {
                'user': user,
                'datas': datas,
                'upload_url':upload_url,
                'login': users.create_login_url(self.request.uri),
                'logout': users.create_logout_url(self.request.uri),
                }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


        
class UploadBlobHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        blob_image = self.get_uploads('delUpload')[0]
        i = Customer(email = str(users.get_current_user()),
                     image_key = str(blob_image.key()),
                     image = blob_image,
                     type = cgi.escape(self.request.get('type')))
        i.put()
        self.redirect('/')


class DownloadBlobImage(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class DelBlobImage(webapp2.RequestHandler):
    def post(self):
        datas = db.GqlQuery("SELECT * FROM Customer")
        for d in datas:
            if cgi.escape(d.image_key)==cgi.escape(self.request.get('key')):
                d.delete()
        self.redirect('/')

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadBlobHandler),
                               ('/download/([^/]+)?', DownloadBlobImage),
                               ('/delapp', DelBlobImage)],
                              debug=True)
