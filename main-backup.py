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

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<div class="main">')
        user = users.get_current_user()
        if user:
            greeting = ("You have signed as, %s (<a href=\"%s\">sign out</a>)" % (user.nickname(),users.create_logout_url("/")))
            upload_url = blobstore.create_upload_url('/upload')
            self.response.out.write("%s" % greeting)
            self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
            self.response.out.write("""Upload BigImage: <input type="file" name="delUpload"> <input type="submit" name="submit" value="Submit"> </form></body></html>""")
            datas = db.GqlQuery("SELECT * FROM Customer")
            self.response.out.write('<br>')
            for d in datas:
                if str(cgi.escape(d.email))==str(user):
                    self.response.out.write('<a href="http://localhost:8084/show/%s">' %(cgi.escape(d.image_key)))
                    self.response.out.write('<img src="http://localhost:8084/show/%s" align="middle" style=position:relative" width="400" height="300"><p></p>' %(cgi.escape(d.image_key)))
                    self.response.out.write('</a>')
                else:
                   pass
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." % users.create_login_url("/"))
            self.response.out.write("%s" % greeting)
    
        self.response.out.write('</div></html>')
        
        template_values = {
                    'greeting': greeting
                }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


        
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        blob_image = self.get_uploads('delUpload')[0]
        i = Customer(email = str(users.get_current_user()),
                     image_key = str(blob_image.key()),
                     image = blob_image)
        i.put()
        self.redirect('/')
        #self.redirect('/show/%s' % blob_info.key())


class ShowHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

class DelBlobImage(webapp2.RequestHandler):
    def get(self,resource):
        resource = str(urllib.unquote(resource))
        self.response.out.write(resource)
#        user = users.get_current_user()
#        datas = db.GqlQuery("SELECT * FROM Customer")
#        for d in datas:
#            if cgi.escape(d.email)==str(user) and cgi.escape(d.image_key)==resource):
#                d.delete()
        self.redirect('/')

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
                               ('/show/([^/]+)?', ShowHandler),
                               ('/delapp', DelBlobImage)],
                              debug=True)
