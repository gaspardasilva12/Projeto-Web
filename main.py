from flask import Flask, render_template
from flask_login import current_user
from website import create_app, create_database

app = create_app()

if __name__ == '__main__':
    create_database(app)
    app.run(debug=True)
