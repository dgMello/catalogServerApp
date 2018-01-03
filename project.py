from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from functools import wraps
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
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web'][
    'client_id']
APPLICATION_NAME = 'Catelog Application'

# Connect to database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state toekon
@app.route('/login')
def showLogin():
    """
    Creates a random state token and renders the login.html template.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Enables login through Facebook using the FB API and creates login session
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Gathers data from Facebook API and places it inside a session variable.
    """
    # Check the state token produced at login.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    # Exchange client token for long-lived server side token.
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web'][
        'app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web'][
        'app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'
        % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = 'https:/graph.facebook.com/v2.11/me'
    # Remove expire tag from token
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = ('https://graph.facebook.com/v2.11/me?access_token=%s&fields=name,id,email'
        % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Get data from API request and assign it to the login session.
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    # Check to see if this a new user. If not create a user profile
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Create an output to diplay username and other info on page.
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += ''' " style = "width: 300px: height: 300px; border-radius:150px;
        -webkit-border-radius: 150px; -moz-border-radius: 150px;">'''
    flash("You are now logged in as %s" % login_session['username'])
    return output

# Method for disconnecting from fabebook
@app.route('/fbdisconnect')
def fbdisconnect():
    """
    Logout Facebook user. Called by disconnect method if the user logged in
    through Facebook.
    """
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have been logged out.'

# Enables login from Google using the Google API and creates a login session
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Gathers data from Goolge Sign In API and places it inside a session
    variable.
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parmeter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    # Upgrade the authorization code into a credentials object
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('''Failed to upgrade the
            authorization code.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET') [1])
    # if there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("""Token's user ID doesn't match
            given user ID."""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'
            ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info from Google account using Google APi.
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    # Assign User info to login session.
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # Check to see if useris new.  If not, create new user.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Display welcome screen.
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += ''' " style = "width: 300px: height: 300px; border-radius:150px;
        -webkit-border-radius: 150px; -moz-border-radius: 150px;">'''
    flash("You are now logged in as %s" % login_session['username'])
    return output

# This method enables the user to disconect from Google or Facebook.
@app.route('/disconnect')
def disconnect():
    """
    Disconnets user from the login session.  Calls fbdisconnect & gdisconnect
    methods.
    """
    # Check that there is a provider in the login session.
    if 'provider' in login_session:
        # Check which provider the user is logged in with.
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        # Delete the current information in the user session.
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']
        # Show the user that they were logged out using a flash message.
        flash('You have successfully been logged out.')
        return redirect(url_for('showCategories'))
    else:
        flash('You were not logged in to begin with!')
        return redirect(url_for('showCategories'))

# Method for creating a new user.
def createUser(login_session):
    """
    Creats a new user in the database using the login session data.
    """
    # Assign data from login session to variable
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    # Add new user to session and commit it.
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    # Return the user ID of the new user.
    return user.id

# Method for getting user info.
def getUserInfo(user_id):
    """
    Get user info using the user's ID.
    """
    # Use a sql search to find the user using their user ID.
    user = session.query(User).filter_by(id=user_id).one()
    # Return user data.
    return user

# Method for getting user ID.
def getUserID(email):
    """
    Get the User ID using the current email of the logged in user.
    """
    # Try to find the user using their email address.
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    # If none is found return None.
    except:
        return None

# Method for creating a wrapper to require a login.
def login_required(func):
    """
    Wrapper to check if the user is logged in.
    """
    @wraps(func)
    def wrapper():
        if 'username' not in login_session:
            return redirect('login')
        else:
            return func()
    return wrapper

# Method for creating a wrapper for checking who owns an item.
def checkUser(func):
    """
    Wrapper to check if item being delete or edited is owend by the user.
    """
    @wraps(func)
    def wrapper(current_item):
        currentItem = session.query(Item).filter_by(name=current_item)\
            .one()
        category = session.query(Category.name).filter_by\
            (id=currentItem.category_id).one()
        if login_session['user_id'] != currentItem.user_id:
            return """<script>  function myFunction() {alert('You are not authorized to made changes to this item. Please create your own items.');
                location.href="http://localhost:8000/catalog/"
                }</script><body onload='myFunction()'>"""
        else:
            return func(currentItem.name)
    return wrapper

# Method for disconnecting from google sign in.
@app.route('/gdisconnect')
def gdisconnect():
    """
    Logout Google user. Called by disconnect method if the user logged in
    through Google.
        """
    # Only disconnect a connected user by checking the access token.
    access_token = login_session.get('access_token')
    print access_token
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token.
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
        % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's session.
        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # If you get a different repsonse from the google server.
        response = make_response(json.dumps('''Failed to revoke token for given
            user''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Method to get JSON APIs of all categories
@app.route('/catalog.json')
def catalogsJSON():
    """
    Return all categories and their information in JSON form.
    """
    # Find all categories than jsonify them.
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories],
        items=[i.serialize for i in items])

# Method to get JSON APIs of the items in a certain category.
@app.route('/catalog/<current_category>.json')
def categoryJSON(current_category):
    """
    Return a certain category and it's items in JSON form.
    """
    # Find a particular category and it's items and jsonify it.
    category = session.query(Category).filter_by(name=current_category).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])

# Method to get JSON APIs of a certain item.
@app.route('/catalog/<current_category>/<current_item>.json')
def itemJSON(current_category, current_item):
    """
    Return a certain item's data in JSON form.
    """
    # Find a particular item and jsonify it.
    item = session.query(Item).filter_by(name=current_item).one()
    return jsonify(item=item.serialize)

# Method to show all categorires & latest items added.
@app.route('/')
@app.route('/catalog/')
def showCategories():
    """
    Render the categories template to show all categore and 5 recent items.
    """
    categories = session.query(Category).order_by(Category.name).all()
    itemCount = session.query(func.count(Item.id))
    recentItems = session.query(Item.name, Category.name).\
        join(Item.category).order_by(Item.id.desc()).limit(5)
    # See if the user is logged in.
    if 'username' not in login_session:
        is_logged_in = False
    else:
        is_logged_in = True
    return render_template('categories.html', categories=categories,
        items=recentItems, is_logged_in=is_logged_in)

# Method to show all items in a category
@app.route('/catalog/<current_category>/items')
def showCategory(current_category):
    """
    Render the category template to show a certain category and all it's items.
    """
    categories = session.query(Category).order_by(Category.name)
    currentCategory = session.query(Category).filter_by\
        (name = current_category.title()).one_or_none()
    # Check to see if the category name in the URL is a valid category.
    if currentCategory == None:
        return abort(404)
    items = session.query(Item).filter_by(category_id=currentCategory.id)
    # See if the user is logged in.
    if 'username' not in login_session:
        is_logged_in = False
    else:
        is_logged_in = True
    return render_template('category.html', items=items,
        category=currentCategory.name, categories=categories,
        is_logged_in=is_logged_in)


# Method to create a new item.
@app.route('/catalog/item/new', methods=['GET', 'POST'])
@login_required
def newItem():
    """
    Render the addItem template to allow a user to create a new item.
    """
    categories = session.query(Category).order_by(Category.name)
    # If a post request is sent to route create a new item.
    if request.method == 'POST':
        categoryID = request.form['categorySelection']
        newItem = Item(name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['categorySelection'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created' % (newItem.name))
        return redirect(url_for('showCategories', categories=categories))
    else:
        return render_template('addItem.html',
            categories=categories)

# Method to show description & name of a certain itme.
@app.route('/catalog/<current_category>/<current_item>')
def showItem(current_category, current_item):
    """
    Render the item template to show a user a particular item's information.
    """
    item = session.query(Item).filter_by(name=current_item).one_or_none()
    # Check to make sure the item in the url is a valid item.
    if item == None:
        return abort(404)
    # See if the user is logged in.
    if 'username' not in login_session:
        is_logged_in = False
    else:
        is_logged_in = True
    return render_template('item.html', item=item,
        is_logged_in=is_logged_in)

# Method to edit an item name, description & category.
@app.route('/catalog/<current_item>/edit', methods=['GET', 'POST'])
@checkUser
def editItem(current_item):
    """
    Renders the editItem template to allow a user to edit an item.
    """
    editedItem = session.query(Item).filter_by(name=current_item).one_or_none()
    # Check to make sure the item in the url is a valid item.
    if editedItem == None:
        return abort(404)
    category = session.query(Category).filter_by\
        (id=editedItem.category_id).one()
    categories = session.query(Category).order_by(Category.name)
    # If a post request is sent to route edite the info of the edited item.
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['categorySelection']:
            editedItem.category_id = request.form['categorySelection']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showItem', current_category=category.name,
            current_item=editedItem.name))
    else:
        return render_template('editItem.html', item=editedItem,
            category=category, categories=categories)

# Method to delete an item.
@app.route('/catalog/<current_item>/delete', methods=['GET', 'POST'])
@checkUser
def deleteItem(current_item):
    """
    Render the deleteitem template to allow a user to delete an item.
    """
    # Search for the item to delete.
    itemToDelete = session.query(Item).filter_by(name=current_item)\
        .one_or_none()
    # Check to make sure the item in the url is a valid item.
    if itemToDelete == None:
        return abort(404)
    category = session.query(Category).filter_by\
        (id=itemToDelete.category_id).one()
    categories = session.query(Category).order_by(Category.name)
    # If a post request is sent to route dlete the item.
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteItem.html', item=itemToDelete,
            category=category, categories=categories)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
