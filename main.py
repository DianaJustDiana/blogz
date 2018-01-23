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

    def __init__(self, title, body):
        self.title = title
        self.body = body

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

            new_entry = Blog(title, body)
            db.session.add(new_entry)
            db.session.flush()
            db.session.commit()

            single_id = new_entry.id
            return redirect("/blog?id={0}".format(single_id))

    return render_template('new_post.html')





        
          
"""
class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #add unique=True so there can't be 2 records with same email
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    #doesn't add column in db, but sets up connection
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

#check to see if user is still logged in
#special function, special decorator -- not a request handler
#this runs before EVERY request and checks ALL incoming requests
@app.before_request
def require_login():
    #whitelist so people not logged in can see login page
    #people not logged in can see these
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        #first part checks if user exists (True) and second part checks if password matches
        if user and user.password == password:
            #remember the user by adding dict key of email
            session['email'] = email
            #add flash message to display to the user
            flash('Logged in')
            return redirect('/')
        else:
            #second parameter is category; it connects to html in base.html
            flash('User password incorrect or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO validate

        #see if user already exists in our db
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            #remember the user by adding dict key of email
            session['email'] = email
            return redirect('/')
        else:
            #TODO tell user they already exist in db
            return "<h1>Duplicate user</h1>"


    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


###Start used pieces of this part
@app.route('/', methods=['POST', 'GET'])
def index():
    
    #specifies that the owner is the user currently signed in
    owner = User.query.filter_by(email=session['email']).first()


    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    #owner=owner means left query for tasks based on the owner property, and right the owner variable defined above
    tasks = Task.query.filter_by(completed=False,owner=owner).all()  
    completed_tasks = Task.query.filter_by(completed=True,owner=owner).all()
    return render_template('todos.html',title="Get It Done!", tasks=tasks, completed_tasks=completed_tasks)
###End used pieces of this part


@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed =  True
    db.session.add(task)
    db.session.commit()

    return redirect("/")

"""

if __name__ == '__main__':
    app.run()
