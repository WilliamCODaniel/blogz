from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash, make_salt

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    post = db.Column(db.Text)

    def __init__(self, name, content):
        self.name = name
        self.post = content

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

#@app.route('/')
#def index():
    

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

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
            new_post = Blog(post_title, post_content)
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