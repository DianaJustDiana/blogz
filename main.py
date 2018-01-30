from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
#This line provides insight into errors.
app.config['DEBUG'] = True
#This line connects my files to the db.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
#This line provides helpful info in the terminal.
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#Need to set secret key when using session.
#I typed this in -- not a real one.
app.secret_key = 'abc123'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    #Limited title to 60 characters for SEO.
    title = db.Column(db.String(60))
    #Limited body to 14,000 characters because that's about 2000 words.
    body = db.Column(db.String(14000))

    #Starts new for blogz
    #Could have named this anything -- didn't have to have _id at the end.
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    #Ends new for blogz

#Starts tweak for blogz
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    #Limited username to 30 characters; arbitrary cutoff.
    username = db.Column(db.String(30))
    #Limited password to 30 characters; arbitrary cutoff.
    password = db.Column(db.String(30))
    #Doesn't add column in db, but sets up relationship.
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
#Ends tweak for blogz

#Starts new for blogz
#Check to see if user is still logged in.
#Special function, special decorator -- not a request handler.
#This runs before EVERY request and checks ALL incoming requests.
@app.before_request
def require_login():
    #Whitelist -- people not logged in can see these:
    #These are the def names, not the /route names.
    allowed_routes = ['login', 'list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    #TODO If a username has no associated blog entries, it shouldn't be a clickable link.
    #This shows every username, regardless of whether that user posted a blog entry.
    #That makes no sense.
    #Need to iterate through users and filter out users whose blogs are not null.
    all_the_users = User.query.all()
    #It's called "users" in the template but "all_the_users" in function.
    return render_template('index.html', users=all_the_users)    

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username_as_entered_in_login_form = request.form['username']
        password_as_entered_in_login_form = request.form['password']
        user_exists_in_db = User.query.filter_by(username=username_as_entered_in_login_form).first()
        #First part checks if user exists (True) and second part checks if password matches.
        if user_exists_in_db:
            if user_exists_in_db.password == password_as_entered_in_login_form:
                #remember the user by adding dict key of username
                session['username'] = username_as_entered_in_login_form
                #add flash message to display to the user
                flash('Logged in')
                return redirect('/newpost')
            #In case user exists (True) but password is wrong.
            else: 
                #second parameter is category; it connects to html in base.html
                flash("Sorry, that's not your password. Try again, please.", 'error')
                #Redisplay the form. Populate the username with the previously entered info.
                return render_template('login.html', username=username_as_entered_in_login_form)

        #In case the user doesn't exist at all.
        else:
            #second parameter is category; it connects to html in base.html
            flash("Hmm. I don't remember that username. Let's get you signed up.", 'error')
            return redirect('/signup')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username_as_entered_in_signup_form = request.form['username']
        password_as_entered_in_signup_form = request.form['password']
        verify = request.form['verify']

        #See if user already exists in db.
        existing_user = User.query.filter_by(username=username_as_entered_in_signup_form).first()
        if existing_user:
            #Tell user they already exist in db.
            flash("I'm sorry, but that username is already taken.", 'error')

            return redirect('/signup')
        
        else:
            #Call validate_input() here. 
            if validate_input(username_as_entered_in_signup_form, password_as_entered_in_signup_form, verify) == True:

                new_user = User(username_as_entered_in_signup_form, password_as_entered_in_signup_form)
                db.session.add(new_user)
                db.session.flush()
                db.session.commit()
                #Remember the user by adding dict key of username.
                session['username'] = username_as_entered_in_signup_form
            
                #####LEFT OFF HERE
                return redirect('/newpost')
            

    return render_template('signup.html')

#No need for highly descriptive variable names here because it's a function.
def validate_input(username, password, verify):
    #username = request.form['username']
    username_error = ""
    #password = request.form['password']
    password_error = ""
    #verify = request.form['verify']
    verify_error = ""
    #Use this on username.
    if len(username) == 0:
        username_error = "Oops! This field can't be empty. Please choose a username 3-30 characters long."
    elif not 3 < len(username) <= 30:
        username_error = "I'm sorry, but your username must be 3-30 characters."
        username = ''
    elif " " in username:
        username_error = "Hmm ... username can't contain a space."
        username = ''

    #Use this on password:
    if len(password) == 0:
        password_error = "Oops! This field can't be empty. Please choose a password 3-30 characters long."
    elif not 3 <= len(password) <= 30:
        password_error = "I'm sorry, but password must be 3-30 characters."  
    elif " " in password:
        password_error = "Hmm ... password can't contain a space."

    #Use this on verify.
    if password != verify and not password_error:
        verify_error = "Whoops! These didn't match. Please try again."

    if not username_error and not password_error and not verify_error:
        return True
    else:
        if username_error:
            flash(username_error, 'error')
        elif password_error:
            flash(password_error, 'error')
        elif verify_error:
            flash(verify_error, 'error')
        return render_template('signup.html', username=username)  

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
        
    user_who_just_added_post = request.args.get("id")
    user_you_want = request.args.get("user_you_want")

    if user_who_just_added_post:
        blog = Blog.query.filter_by(id=user_who_just_added_post).first()
        return render_template("most_recent_single_post.html", blog=blog)
    elif user_you_want:
        blogs = Blog.query.filter_by(owner_id=user_you_want).all()
        return render_template('all_posts_of_one_user.html', title="hmm", blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('list_of_all_blog_posts.html', title="Grr", blogs=blogs)
#Ends new for blogz

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    #Starts new for blogz
    #Specifies that the owner is the user currently signed in.
    current_user_is_owner_of_blog_post = User.query.filter_by(username=session['username']).first()
    #Ends new for blogz

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        if len(title) == 0 and len(body) == 0:
            flash("Whoa, slow down! You were a little quick to hit that button.", 'error')
            return render_template('create_new_post.html')        
        elif len(title) == 0:
            flash('Oops! You forgot to put a title on your blog entry.', 'error')
            return render_template('create_new_post.html', body=body)
        elif len(body) == 0:
            flash('Not so fast! Nice title, but where is your body copy?', 'error')
            return render_template('create_new_post.html', title=title)

        else:
            #Starts tweak for blogz
            new_entry = Blog(title, body, current_user_is_owner_of_blog_post)
            #Ends tweak for blogz

            db.session.add(new_entry)
            db.session.flush()
            db.session.commit()

            newest_post = new_entry.id
            return redirect("/blog?id={0}".format(newest_post))

    return render_template('create_new_post.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
