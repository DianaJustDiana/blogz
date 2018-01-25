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
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        #First part checks if user exists (True) and second part checks if password matches.
        if user:
            if user.password == password:
                #remember the user by adding dict key of username
                session['username'] = username
                #add flash message to display to the user
                flash('Logged in')
                return redirect('/newpost')
            #In case user exists (True) but password is wrong.
            else: 
                #second parameter is category; it connects to html in base.html
                flash("Sorry, that's not your password. Try again, please.", 'error')
                #Redisplay the form. Populate the username with the previously entered info.
                return render_template('login.html', username=username)

        #In case the user doesn't exist at all.
        else:
            #second parameter is category; it connects to html in base.html
            flash("Hmm. I don't remember that username. Let's get you signed up.", 'error')
            return redirect('/signup')

    return render_template('login.html')
#Ends new for blogz

@app.route('/blog', methods=['POST', 'GET'])
def index():

    single_id = request.args.get("id")
    if single_id:
        blog = Blog.query.filter_by(id=single_id).first()
        return render_template("single_post.html", blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template('index.html', title="Grr", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        if len(title) == 0 and len(body) == 0:
            flash("Whoa, slow down! You were a little quick to hit that button.", 'error')
            return render_template('new_post.html')        
        elif len(title) == 0:
            flash('Oops! You forgot to put a title on your blog entry.', 'error')
            return render_template('new_post.html', body=body)
        elif len(body) == 0:
            flash('Not so fast! Nice title, but where is your body copy?', 'error')
            return render_template('new_post.html', title=title)

        else:
            #Starts tweak for blogz
            new_entry = Blog(title, body, owner)
            #Ends tweak for blogz

            db.session.add(new_entry)
            db.session.flush()
            db.session.commit()

            single_id = new_entry.id
            return redirect("/blog?id={0}".format(single_id))

    return render_template('new_post.html')

if __name__ == '__main__':
    app.run()
