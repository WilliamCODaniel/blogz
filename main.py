from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash, make_salt
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    post = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, content, owner):
        self.name = name
        self.post = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

@app.route('/')
def index():

    user_id = request.args.get('id')

    users = User.query.all()

    if user_id:
        for user in users:
            if int(user_id) == user.id:
                return render_template('index.html', user=user)
    return render_template('index.html', title="Users", users=users)

@app.before_request
def require_login():
    allowed_routes = ['login', 'user_signup', 'blog', 'index']
    if request.endpoint not in  allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash('Logged in')
            return redirect ('/newpost')
        elif not email:
            flash('No Email entered')
            email = ''
        elif not password:
            flash('No Password entered')
            password = ''
        elif check_pw_hash(password, user.pw_hash) != password:
            flash('Incorrect Password')
            email = email
            return redirect('/login')
        elif not user:
            flash('User does not exist')
            return redirect('/signup')

    return render_template('login.html')     

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def user_signup():


    pass_error = ""
    pass_error2 = ""
    email_error = ""
    special = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']

        if not password:
            pass_error = "No Password entered"
            password = ""
        elif len(password) < 3:
            pass_error = """Password length must be more than 3 and less than
            20 characters"""
            password = ""
        elif len(password) > 20:
            pass_error = """Password length must be more than 3 and less than
            20 characters"""
            password = ""
        elif ' ' in password:
            pass_error = "Password cannot contain spaces"
            password = ""
        elif special.search(password)== None:
            pass_error = "Password must contain at least 1 Special character"
            password = ""
        else:
            dot = 0
            at = 0
            hasnumber = False
            for char in password:
                if char.isdigit():
                    hasnumber = True
            if not hasnumber:
                    pass_error = "Password must contain at least 1 number"
            for char in email:
                if char == '.':
                    dot += 1
                if char == '@':
                    at += 1
                    if dot or at > 1:
                        email_error = "Must contain only one '.' and one '@'."
                        email = email
        if not pass_error:
            if password2 != password:
                pass_error2 = "Passwords do not match"
                password2 = ""
        if pass_error:
            password2 = ""
        if not email:
            email_error = "No Username entered"
            email = ""
        elif len(email) < 3:
            email_error = """Email length must be more than 3 and less than
            20 characters"""
            email = email
        elif len(email) > 20:
            email_error = """Email length must be more than 3 and less than
            20 characters"""
            email = email
        elif ' ' in email:
            email_error = "Email cannot contain spaces"
            email = email
        elif ('.' or '@') not in email:
            email_error = "Not a valid email address"
            email = email
        
        if pass_error or pass_error2 or email_error:
            print (password, password2)
            return render_template ('signup.html', title="Signup",
            pass_error=pass_error, pass_error2=pass_error2, email_error=email_error,
            password=password, password2=password2, email=email)
        if not pass_error or pass_error2 or email_error:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/newpost')

    return render_template ('signup.html', title="Signup")


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    #make sure to fix the session stuff!
    owner = User.query.filter_by(email=session['email']).first()

    title_error = ''
    content_error = ''
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        if not post_title:
            title_error = 'No Title entered'
            post_title = ''      
        if not post_content:
            content_error = 'No post content'
            post_content = ''
        else:
            new_post = Blog(post_title, post_content, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/single-post')

    posts = Blog.query.all()

    if title_error or content_error:
        return render_template('new_post.html', title="New Blog Post",
            posts=posts, title_error = title_error, content_error = content_error)

    return render_template('new_post.html', title="New Blog Post")

@app.route('/blog')
def blog():

    blog_id = request.args.get('id')

    posts = Blog.query.all()


    if blog_id:
        for post in posts:
            if int(blog_id) == post.id:
                return render_template('single_post.html', post=post)

    return render_template('blog.html', title="Blog Posts", posts=posts)



@app.route('/single-post', methods=['POST', 'GET'])
def single_post():

    posts = Blog.query.order_by(Blog.id.desc())
    return render_template('single_post.html', title="New Post", post=posts[0])

if __name__ =='__main__':
    app.run()