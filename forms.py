from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

# Create form to register new users
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign up")

# Form for login
class Login(FlaskForm):
    username= StringField("Username", validators=[DataRequired()])
    password= PasswordField("Password", validators=[DataRequired()])
    submit= SubmitField("Login In")

# WTForm for creating a post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    # author = StringField("Author", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# WTForm for comments
class Comments(FlaskForm):
    comment_text = CKEditorField("Comment:", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")