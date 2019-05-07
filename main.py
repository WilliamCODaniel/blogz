from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    post = db.Column(db.Text)

    def __init__(self, name, content):
        self.name = name
        self.post = content

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        new_post = Blog(post_title, post_content)
        db.session.add(new_post)
        db.session.commit()
    
    posts = Blog.query.all()

    return render_template('blog_post.html', title="New Blog Post",
        posts=posts)


if __name__ =='__main__':
    app.run()