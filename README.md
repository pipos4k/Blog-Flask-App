# 📝 My Blog with Flask
This is a simple blog website made with Flask, SQLAlchemy, and Bootstrap.
Users can read blog posts and write comments. Only admin users can add, edit, or delete posts.

## Features

- GET / - Show all blog posts on the home page
- GET/POST /post/<id> – View a single post and add comments (if logged in)
- GET/POST /new-post -  Create a new post (Admin only)
- GET/POST /edit-post/<id> - Edit a post (Admin only)
- GET /delete/<id> – Delete a post (Admin only)
- GET/POST /register - Register a new user
- GET/POST /login - Log in as a user
- GET /logout - Log out
- GET /about - About page
- GET /contact - Contact page
---

## Technologies Used

- Python 3
- Flask
- SQLAlchemy
- WTForms
- Jinja2 / Bootstrap

---

## Database
This project uses an SQLite database file called posts.db.
There are 3 tables:
- Posts
- Users
- Comments
  
## Setup and Running

1. Clone the repo
2. Install the required packages `(pip install -r requirements.txt)`
3. Create a `.env` file with your API key: `SECRET_KEY=your_api_key`
4. Run the app: `python app.py`
5. Access API endpoints at `http://localhost:5000`

---

Feel free to contribute, report bugs, or suggest new features!
Thanks for checking out the project!

## About this project

This blog is part of the 100 Days of Code course by Angela Yu on Udemy.
I made it to practice building REST APIs using Flask and other tools.
I focused more on backend and security with Werkzeug than on design and CSS.

Note: The contact page is not active by default.
You can set it up using this form service: [Start Bootstrap Contact Forms](https://startbootstrap.com/solution/contact-forms)
