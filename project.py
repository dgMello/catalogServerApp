from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Create Client ID.
# CLIENT_ID = json.loads(
    # open('client_secrets.json', 'r').read())['web']['client_id']
# APPLICATION_NAME = 'Catelog Application'

#Connect to database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# 1 Create anti-forgery state toekon - UNFINISHED & UNTESTED

# 2 Facebook login methods - UNFINISHED & UNTESTED

# 3 Method for dissconnecting from fabebook - UNFINISHED & UNTESTED

# 4. Google login method - UNFINISHED & UNTESTED

# 5.  Method for created a user. - UNFINISHED & UNTESTED

# 6. Method for getting user info. - UNFINISHED & UNTESTED

# 7. Method for getting user ID. - UNFINISHED & UNTESTED

# 8. Method for dissconnecting from google sign in. - UNFINISHED & UNTESTED

# 9. Method to get JSON APIs of the categories. - UNFINISHED & UNTESTED

# 10. Method to get JSON APIs of the items in a certain category. - UNFINISHED & UNTESTED

# 11.  Method to show all categorires & latest items added. - UNTESTED
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by((Category.name))
    if 'username' not in login_session:
        return render_template('publicCategories.html', categories=categories)
    else:
        return render_template('categories.html', categories=categories)

# 12. Method to show all items in a category - UNTESTED
@app.route('/catalog/<int:category_id>/items')
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

# 13. Method to add an item. - UNFINISHED & UNTESTED
@app.route('/catalog/<int:category_id>/add', methods=['GET', 'POST'])
def addItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] != category.user_id:
        return """<script>function myFunction() {alert('You are not authorized
            to add menu items to this restaurant. Please create your own
            restaurant in order to add items.');}</script><body
            onload='myFunction()'>"""
        if request.method == 'POST':
            newItem = Item(name=request.form['name'],
            description=request.form['description'], category_id=category_id,
            user_id=restaurant.user_id)
            session.add(newItem)
            session.commit()
            flash('New Menu %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showCategory', category_id=category_id))
        else:
            return render_template('addItem.html', category_id=category_id)
# 14. Method to show descrition of a certain itme. - UNFINISHED & UNTESTED

# 15. Method to edit an item name & description.- UNFINISHED & UNTESTED

# 16. Method to delete an item. - UNFINISHED & UNTESTED

if __name__ == '__main__':
    app.secrect_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
