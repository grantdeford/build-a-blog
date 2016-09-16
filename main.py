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
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname('_file_'), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
#Text property is over 500 char
#    def render(self):
#        return render_str("post.html", p = self)
#    def render(self):
        #self.render(subject=subject, content=content)
class Initial(Handler):
    def get(self):
        self.render('base.html')

#    def post(self):
#        subject = self.request.get('subject')
#        content = self.request.get('content')
#        self.write(subject, content)


class MainBlog(Handler):
#    def list_post(self, subject="", content="", created=""):with self.render+get
    def get(self):
        results = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        results_order = {"results" : results}
        self.render('mainblog.html', **results_order)
#        self.render('mainblog.html', subject=subject, content=content,
#                    created=created, results=results)
########self.get_posts(limit, offset)
#    def get(self):
#        self.render list_post()
        #not using base.html

class NewPost(Handler):
    def get(self):
        self.render('newpost.html')
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        created = self.request.get('created')

        if subject and content: #and created:
            user_post = Post(subject=subject, content=content)#, created=created)
            #do you have to add date?calling on Post db model
            user_post.put()
            self.redirect('/blog/%s' % str(user_post.key().id()))
        else:
            error = "You need a subject and content." # and a date."
            self.render('newpost.html', subject=subject, content=content, error=error)
#           just self.render('newpost.html')??????

class ViewPostHandler(Handler):#webapp2.RequestHandler
    def get(self, id):
        post = Post.get_by_id(int(id))
        if not post:
            self.error(404)
            return
            #self.render("Wrong" % id)
        self.render("permalink.html", post = post)##permalink.html had mainblog.html

#def get_posts(limit, offset):
#    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5 OFFSET count")
#    return posts()

app = webapp2.WSGIApplication([
    ('/', Initial),
#    ('/mainblog', MainBlog),
    ('/blog', MainBlog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
