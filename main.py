from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blogpost', backref='owner'
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


class Blogpost(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    posted = db.Column(db.DateTime, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.user_id = owner
        self.posted = posted

    def __repr__(self):
        return '<Blogpost %r>' % self.title


@app.route('/') 
def index():
    users = User.query.all()
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    entry_id = request.args.get('id')
    user_id = request.args.get("user")
    page = request.args.get("page", 1, type=int)
    per_page = 5

    if entry_id == None:
        posts = Blogpost.query.all()
        return render_template('blog.html', posts=posts, title='Build-a-blog')
    else:
        posts = Blogpost.query.get(entry_id)
        return render_template('newpage.html', posts=posts, title='Blog Entry')

 

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        newpost_title = request.form['title']
        newpost_body = request.form['body']
        
        if newpost_title == "" and newpost_body == "":
            return render_template('newpost.html', title_error = 'Please fill in the title.', 
            body_error = 'Please fill in the body.')
        if newpost_title == "":
            return render_template('newpost.html', title_error = 'Please fill in the title.')
        if newpost_body == "":
            return render_template('newpost.html', body_error = 'Please fill in the body.')
        newpost = Blogpost(newpost_title, newpost_body)
        db.session.add(newpost)
        db.session.commit()
        return redirect('/blog?id={}'.format(newpost.id))
    return render_template('newpost.html')




if __name__ == '__main__':
    app.run()