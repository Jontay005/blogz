from flask import Flask, request, redirect, render_template, session, flash, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True #output in terminal 
db = SQLAlchemy(app) #create db object
app.secret_key = '2ndjEE4tKn'
 
class Blog(db.Model):     #create Blog class 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, owner, pub_date=None): #constructor
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.now()
        self.pub_date = pub_date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(120), unique=True) #make unique ****************
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')        

@app.route("/login", methods=['POST', 'GET'])   
def login():
    if request.method == 'POST':
        username = request.form['username'] #python dic containing POST data
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged In') #use the session obj to store the msg till user comes back
            print(session)
            return redirect('/')
        else: 
            flash('Password Incorrect or User Does Not Exist', 'error')
    return render_template('login.html')  

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route("/signup", methods=["POST", "GET"])   
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']


        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if ' ' not in username and ( len(username) > 2 and len(username) < 20):
                if ' ' not in password  and ( len(password) > 2 and len(password) < 20):
                    if password == verify:
                        new_user = User(username, password)   
                        db.session.add(new_user)
                        db.session.commit()
                        session['username'] = username
                        return redirect('/newpost')
                    else:
                        flash("passwords do not match", 'error')
                else:
                    flash("password must b btw 3 and 20 chars and no space", 'error')   
            else:
                flash("username must b btw 3 and 20 chars and no space", 'error')                     
        else:
            flash("User already exists", 'error' )
    return render_template('signup.html')   

@app.route("/", methods=[ "GET"])
def index():
    #owner = User.query.filter_by(username = session['username']).first() 
    #owner_name = owner.username
    users = User.query.all()
    print(users)

    #blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('index.html', users=users) 
    
@app.route("/blog", methods=["GET"])   
def blog():
    user_id = request.args.get('user_id')
    
    if user_id:
        user = User.query.get(user_id) #added
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html', blogs=blogs, user=user)
    else:
        #get all the blogs
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build A Blog", blogs=blogs)

@app.route("/blogpost", methods=["GET"])
def blogpost():
    
    #TODO confirm this
    
    blog_id = request.args.get('id') #get blog id
    blog = Blog.query.get(blog_id) #use primary keuuse get #get blog with passed 
    user_id = blog.owner_id #get user id
    user = User.query.filter_by(id=user_id).first() #get actual username


    
    return render_template('blogpost.html', blog=blog, user=user)

@app.route("/newpost", methods=["POST", "GET"])    
def newpost():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']
        owner = User.query.filter_by(username = session['username']).first()
        new_blog = Blog(blog_title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        id = new_blog.id
        return redirect(url_for("blogpost", id=id)) #pass primitive type
    else:
        return render_template("/newpost.html")
    
if __name__ == '__main__':
    app.run()