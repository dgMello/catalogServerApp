from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Items
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Catelog Appliction'

#Connect to database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# 1 Create anti-forgery state toekon - UNFINISHED

# 2 Facebook login methods - UNFINISHED

# 3 Method for dissconnecting from fabebook - UNFINISHED

# 4. Google login method - UNFINISHED

# 5.  Method for created a user. - UNFINISHED

# 6. Method for getting user info. - UNFINISHED

# 7. Method for getting user ID. - UNFINISHED

# 8. Method for dissconnecting from google sign in. - UNFINISHED

# 9. Method to get JSON APIs of the categories. - UNFINISHED

# 10. Method to get JSON APIs of the items in a certain category. - UNFINISHED

# 11.  Method to show all categorires & latest items added. - UNFINISHED
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('publicCategories.html', categories=categories)
    else:
        return render_template('categories.html', categories=categories)

# 12. Method to show all items in a category - UNFINISHED
@app.route('/catalog/<int:category_id>/')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    items = session.query(Item).filter_by(category_id=category_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicCategory.html', items=items,
            category=category, creator=creator)
    else:
        return render_templates('category.html', items=items, category=category,
            creator=creator)

# 13. Method to add an item. - UNFINISHED

# 14. Method to show descrition of a certain itme. - UNFINISHED

# 15. Method to edit an item name & description.- UNFINISHED

# 16. Method to delete an item. - UNFINISHED

if __name__ == '__main__':
    app.secrect_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
