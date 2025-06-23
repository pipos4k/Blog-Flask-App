from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey
from forms import RegisterForm, Login, Comments, CreatePostForm
from datetime import date
from functools import wraps

# Create Flask app
app = Flask(__name__) 
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
# Initialise the CKEditor so that you can use it in create_post.html
app.config['CKEDITOR_SERVE_LOCAL'] = False
app.config['CKEDITOR_PKG_TYPE'] = "standard" 
app.config['CKEDITOR_CDN'] = None
Bootstrap5(app)
ckeditor = CKEditor(app=app)

# * Create admin decorator
def admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id != 1 return 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function (home_page)
        return f(*args, **kwargs)
    return decorated_function
# * end of admin

# * Create database for posts
class Base(DeclarativeBase): 
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app=app)

# Configure table
class Posts(db.Model):
    __tablename__ = "blog_post" # Link to the actual table name in DB

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author= relationship("User", back_populates="posts")

    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

# New table for comments
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # Add child relationship with User class
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

# * end of db

# * Create USER

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    
    #This will act like a List of Posts objects attached to each User. 
    #The "author" refers to the author property in the Posts class.
    posts= relationship("Posts", back_populates="author")

    # Add parent relationship with Comment class
    comments = relationship("Comment", back_populates="comment_author")

# Set up Login
login_manager = LoginManager()
login_manager.init_app(app=app) # Connect with app

# Load user by ID
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id) # Call out user or return 404
# * end of create user



# * Handle users
from werkzeug.security import generate_password_hash, check_password_hash
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check the username if already exists
        result= db.session.execute(db.select(User).where(User.email == form.email.data))
        user= result.scalar()
        if user: 
            # User already exists
            flash("Username already exists, try to login")
            return redirect(url_for("login"))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method="scrypt",
            salt_length=8
        )
        new_user = User(
            username= form.username.data,
            email= form.email.data,
            password= hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()

        # Authenticate the user with FlaskLogik
        login_user(new_user)
        return redirect(url_for("home_page"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = Login()
    if form.validate_on_submit():

        password= form.password.data
        result= db.session.execute(db.select(User).where(User.username == form.username.data))
        user= result.scalar() # Username is unique so will have one result only.

        if not user:
            flash("That username doesn't exixt, please enter a valid accoutn")
            return(redirect(url_for("login")))
        elif not check_password_hash(user.password, password):
            flash("Password is incorrect!")
            return(redirect(url_for("login")))
        else:
            login_user(user)
            return redirect(url_for("home_page"))
    return render_template("login.html", form=form, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))

# * end of handle users

# * Start the app
# Define the route
@app.route("/") 
def home_page():
    # Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(Posts))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, current_user=current_user)

# * Handle POSTS, GET, DELETE, EDIT
#Define a page for individual post by ID  
@app.route("/post/<int:index>")
def show_post(index):
    result = db.get_or_404(Posts, index)
    # Add comment form
    comment_form = Comments()
    return render_template("post.html", post=result, current_user=current_user, form=comment_form)

# Create a new post page, ONLY ADMIN
@app.route("/new-post", methods=["GET", "POST"])
@admin
def add_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = Posts(
            title= form.title.data,
            subtitle= form.subtitle.data,
            body= form.body.data,
            img_url = form.img_url.data,
            author= current_user,
            date= date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home_page"))
    return render_template("create_post.html", form=form, current_user=current_user)

# Edit a post by id, ONLY ADMIN
@app.route("/edit-post/<int:index>", methods=["GET", "POST"])
@admin
def edit_post(index):
    result = db.get_or_404(Posts, index)
    edit_form = CreatePostForm(
        title= result.title,
        subtitle= result.subtitle,
        img_url= result.img_url,
        author= result.author,
        body= result.body
    )

    if edit_form.validate_on_submit():
        result.title= edit_form.title.data
        result.subtitle= edit_form.subtitle.data
        result.img_url= edit_form.img_url.data
        result.author= current_user
        result.body= edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", index=result.id))
    return render_template("create_post.html", form=edit_form, is_edit=True, current_user=current_user)

# Delete post, ONLY ADMIN
@app.route("/delete/<int:index>")
@admin
def delete_post(index):
    result = db.get_or_404(Posts, index)
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for("home_page"))
# * end of handle posts



# Define the about page
@app.route("/about")
def about_page():
    return render_template("about.html", current_user=current_user)

# Define the about page
@app.route("/contact")
def contact_page():
    return render_template("contact.html", current_user=current_user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

