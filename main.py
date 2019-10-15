from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blogpost', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    
class Blogpost(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        

    
@app.route('/') 
def index():
    users = User.query.all()
    return render_template('index.html', users=users, header='Blog Users')

@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify_password = request.form["verify_password"]
        #no_error = True
        username_error = ""
        password_error = ""
        password_error2 = ""
        errors = ""
        if (len(username) < 3 or len(username) > 20) or ((not username) or username.strip() == "") or " " in username: 
            username_error = "Username MUST be between 3-20 characters long and cannot have any spaces."
            errors += username_error
            #no_error = False
        if (len(password) > 20 or len(password) < 3) or (" " in password) or ((not password) or password.strip() == ""):
            password_error = "Password MUST be between 3-20 characters long and cannot have any spaces."
            errors += password_error
            #no_error = False
        if verify_password != password:
            password_error2 = "Make sure password is the same in both boxes."
            errors += password_error2
            
            
        if errors:
            
            return redirect('/signup')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
    return render_template('/signup.html')

@app.before_request
def require_login():
    allowed_routes =["login", "signup", "index"]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('User password is incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/blog')
def blog():
    posts = Blogpost.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    if user_id:
        posts = Blogpost.query.filter_by(user_id=user_id)
        user = User.query.filter_by(id=user_id).first()
        return render_template('user.html', posts=posts, user=user)
    elif blog_id:
        post = Blogpost.query.get(blog_id)
        return render_template('newpage.html', post=post)
    else: 
        user = User.query.filter_by(id=user_id)
        return render_template('blog.html', posts=posts, user=user, header='All Blog Posts')
 

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        newpost_title = request.form['title']
        newpost_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if newpost_title == "" and newpost_body == "":
            return render_template('newpost.html', title_error = 'Please fill in the title.', 
            body_error = 'Please fill in the body.')
        if newpost_title == "":
            return render_template('newpost.html', title_error = 'Please fill in the title.')
        if newpost_body == "":
            return render_template('newpost.html', body_error = 'Please fill in the body.')
        newpost = Blogpost(newpost_title, newpost_body, owner)
        db.session.add(newpost)
        db.session.commit()
        return redirect('/blog?id={}'.format(newpost.id))
    return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()