from flask import Flask, render_template, redirect, url_for, request, session, abort, flash
from database import Database
from base64 import b64encode 
from os import urandom
from time import sleep
import imp
pwds = imp.load_source('pwds', '../pwds.py')


app = Flask(__name__)

app.config['DEBUG'] = True
'''
Login handler
'''
@app.route('/login', methods=['POST','GET'])
def do_admin_login():
    if session.get('logged_in') == True:
        return ("Already logged in")

    if request.method == 'POST':
        for user in pwds.Users:
            if user[0] == request.form['username'] and user[1] == request.form['password']:
                session['logged_in'] = True
                flash('You logged in!')
                return redirect('/success')
        return render_template('login.html')

    else:
        return render_template('login.html')

'''
Logout Handler
'''
@app.route('/logout')
def logout():
    session['logged_in'] = False
    return ("Logged out")


'''
Show Posts:
This shows different posts by taking a varable as the post title, getting the post from the database
and displaying it.
'''
@app.route('/posts/<title>')
def showPost(title):
    db = Database()
    post = db.findPost(title)
    if post == None:
        return "Error retriving post"
    
    encoded_img = b64encode(post.image).decode('utf-8').replace('\n', '')
    img_tag = '<img src="data:image;base64,{0}">'.format(encoded_img)
    return img_tag 
 
'''
Show something was sucessful 
'''
@app.route('/success/')
def success():
    return 'SUCCESS' 

'''
Edit post
Takes a variable as the title of the post to edit
Allow them to delete the post.
'''
@app.route('/editPost/<title>', methods = ['POST', 'GET'])
def editPost(title):
    #Only admin here
    if not session.get('logged_in'):
        return render_template('login.html')

    db = Database() 
    #This is a request to edit a post with included data
    if request.method == 'POST':
        if 'Submit' in request.form:
            title_edit = request.form['title']
            description_edit = request.form['description']
            image_edit = request.files['image']
            result = db.editPost(title,title_edit,description_edit,image_edit)
            if result == True:
                return redirect(url_for('success')) 
            else:
                return "FAILED EDIT"
        elif 'Delete' in request.form:
            result = db.deletePost(title)
            if result == True:
                return redirect(url_for('success')) 
            else:
                return "FAILED EDIT"
        else:
            return "BAD DESIGNER was resposible for this"
    #Someone wants to view a post to edit
    else:
        post = db.findPost(title)
        if post == None:
            return "ERROR: Post not found"
        else:
            img_tag = b64encode(post.image).decode('utf-8').replace('\n', '')
            return render_template('editPost.html',title=post.title, description=post.description, img_tag=img_tag)
 
'''
Allow a user to add a post to the database
User must be logged in
'''
@app.route('/addPost', methods = ['POST', 'GET'])
def addPost():
    #Only admins here
    if not session.get('logged_in'):
        return render_template('login.html')

    #Someone has entered data?
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        #Check to see if image was returned
        if 'image' not in request.files:
            return render_template('addPost.html')
        image = request.files['image']
        if image.filename == "":
            return render_template('addPost.html')

        image = image.read()   
        db = Database()
        db.addPost(title,body,image)

        return redirect(url_for('success'))

    #Someone wants the page to attempt to enter data
    if request.method == 'GET':
        return render_template('addPost.html')

'''
Main landing page
'''
@app.route('/')
def main():
    if session.get('logged_in'):
        db = Database()
        posts = db.getAllPosts()
        posts = [{key: value for (key, value) in post.items()} for post in posts] 
        for post in posts:
            post['image'] = b64encode(post['image']).decode('utf-8').replace('\n', '') 
        return render_template('homepage.html', posts=posts)
    else:
        return render_template('comingsoon.html')

if __name__ == '__main__':
    app.secret_key = urandom(pwds.KeySeed)
    app.run(host='0.0.0.0', port=5000, debug=True)
