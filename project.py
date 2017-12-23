from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, func, desc
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
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Catelog Application'

# Connect to database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# 1 Create anti-forgery state toekon - UNFINISHED & UNTESTED
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# 2 Facebook login methods - UNFINISHED & UNTESTED

# 3 Method for dissconnecting from fabebook - UNFINISHED & UNTESTED

# 4. Google login method - UNFINISHED & UNTESTED

# 5.  Method for created a user. - UNTESTED
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# 6. Method for getting user info. -  UNTESTED
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# 7. Method for getting user ID. - UNTESTED
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# 8. Method for dissconnecting from google sign in. - UNFINISHED & UNTESTED

# 9. Method to get JSON APIs of all categories
@app.route('/catalog.json')
def catalogsJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])

# 10. Method to get JSON APIs of the items in a certain category.
@app.route('/catalog/<current_category>.json')
def categoryJSON(current_category):
    category = session.query(Category).filter_by(name=current_category).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])

# 11. Method to get JSON APIs of a certain item.
@app.route('/catalog/<current_category>/<current_item>.json')
def itemJSON(current_category, current_item):
    item = session.query(Item).filter_by(name=current_item).one()
    return jsonify(item=item.serialize)

# 12.  Method to show all categorires & latest items added.
@app.route('/')
@app.route('/catalog/')
def showCategories():
    login_session = 'Doug Mello'
    categories = session.query(Category).order_by(Category.name)
    itemCount = session.query(func.count(Item.id))
    recentItems = session.query(Item.name, Category.name).\
        join(Item.category).order_by(Item.id.desc()).limit(5)
    if 'username' not in login_session:
        return render_template('publicCategories.html', categories=categories,
            items=recentItems)
    else:
        return render_template('categories.html', categories=categories,
            items=recentItems)

# 13. Method to show all items in a category
@app.route('/catalog/<current_category>/items')
def showCategory(current_category):
    categories = session.query(Category).order_by(Category.name)
    currentCategory = session.query(Category).filter_by\
        (name = current_category.title()).one()
    creator = getUserInfo(currentCategory.user_id)
    items = session.query(Item).filter_by(category_id=currentCategory.id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicCategory.html', items=items,
            creator=creator, category=currentCategory,
            categories=categories)
    else:
        return render_templates('category.html', items=items, creator=creator,
            category=currentCategory.name, categories=categories)


# 14. Method to add an item
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    categories = session.query(Category).order_by(Category.name)
    # if 'username' not in login_session:
    #     return redirect('/login')
    # if login_session['user_id'] != category.user_id:
        # return """<script>function myFunction() {alert('You are not authorized
            # to add menu items to this restaurant. Please create your own
            # restaurant in order to add items.');}</script><body
            # onload='myFunction()'>"""
    # Indent this section after finishing the above section.
    if request.method == 'POST':
        categoryID = request.form['categorySelection']
        categoryUserID = session.query(Category.user_id).filter\
            (Category.id==categoryID)
        newItem = Item(name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['categorySelection'],
            user_id=categoryUserID)
        session.add(newItem)
        session.commit()
        # flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showCategories', categories=categories))
    else:
        return render_template('addItem.html',
            categories=categories)

# 15. Method to show description of a certain itme.
@app.route('/catalog/<current_category>/<current_item>')
def showItem(current_category, current_item):
    category = session.query(Category).filter_by\
        (name = current_category.title())
    item = session.query(Item).filter_by(name=current_item).one()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicItem.html', item=item)
    else:
        return render_template('item.html', item=item)
# creator=creator

# 16. Method to edit an item name & description.
@app.route('/catalog/<current_item>/edit', methods=['GET', 'POST'])
def editItem(current_item):
    # if 'username' not in login_session:
    #    return redirect('/login')
    editedItem = session.query(Item).filter_by(name=current_item).one()
    category = session.query(Category).filter_by\
        (id=editedItem.category_id).one()
    categories = session.query(Category).order_by(Category.name)
    # if login_session['user_id'] != category.user_id:
    #     return """<script>function myFunction() {alert('You are not authorized
    #         to edit menu items to this restaurant. Please create your own
    #         restaurant in order to edit items.');}</script><body
    #         onload='myFunction()'>"""
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['categorySelection']:
            editedItem.category_id = request.form['categorySelection']
        session.add(editedItem)
        session.commit()
        # flash('Menu Item Successfully Edited')
        return redirect(url_for('showItem', current_category=category.name,
            current_item=editedItem.name))
    else:
        return render_template('editItem.html', item=editedItem,
            category=category, categories=categories)

# 17. Method to delete an item.
@app.route('/catalog/<current_item>/delete', methods=['GET', 'POST'])
def deleteItem(current_item):
    # if 'username' not in login_session:
    #     return redirect('/login')
    itemToDelete = session.query(Item).filter_by(name=current_item).one()
    category = session.query(Category).filter_by\
        (id=itemToDelete.category_id).one()
    categories = session.query(Category).order_by(Category.name)
    # if login_session['user_id'] != category.user_id:
    #     return """<script>function myFunction() {alert('You are not authorized
    #         to edit menu items to this restaurant. Please create your own
    #         restaurant in order to edit items.');}</script><body
    #         onload='myFunction()'>"""
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        # flash('Item Successfully Deleted')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteItem.html', item=itemToDelete,
            category=category, categories=categories)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
