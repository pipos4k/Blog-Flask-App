from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

# Create Flask app
app = Flask(__name__) 
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
# Initialise the CKEditor so that you can use it in create_post.html
app.config['CKEDITOR_SERVE_LOCAL'] = False
app.config['CKEDITOR_PKG_TYPE'] = "standard" 
app.config['CKEDITOR_CDN'] = None
Bootstrap5(app)
ckeditor = CKEditor(app=app)

# * Create database
class Base(DeclarativeBase): 
    pass
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app=app)

# Configure table
class Posts(db.Model):
    __tablename__ = "blog_post" # Link to the actual table name in DB

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

# Create a WTForm 
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
# * end of db

# * Create USER
from forms import RegisterForm
class User(db.Model): # UserMixin
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    pass

# * end of create user

# Define the route
@app.route("/") 
def home_page():
    # Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(Posts))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)

#Define a page for individual post by ID  
@app.route("/post/<int:index>")
def show_post(index):
    result = db.get_or_404(Posts, index)
    return render_template("post.html", post=result)

# Create a new post page
@app.route("/new-post", methods=["GET", "POST"])
def add_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = Posts(
            title= form.title.data,
            subtitle= form.subtitle.data,
            body= form.body.data,
            img_url = form.img_url.data,
            author= form.author.data,
            date= date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home_page"))
    return render_template("create_post.html", form=form)

# Edit a post by id
@app.route("/edit-post/<int:index>", methods=["GET", "POST"])
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
        result.author= edit_form.author.data
        result.body= edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", index=result.id))
    return render_template("create_post.html", form=edit_form, is_edit=True)

# Delete post
@app.route("/delete/<int:index>")
def delete_post(index):
    result = db.get_or_404(Posts, index)
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for("home_page"))

# Define the about page
@app.route("/about")
def about_page():
    return render_template("about.html")

# Define the about page
@app.route("/contact")
def contact_page():
    return render_template("contact.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

