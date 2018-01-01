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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# This method enables login through Facebook.
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
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
    # Get data from API request
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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += ''' " style = "width: 300px: height: 300px; border-radius:150px;
        -webkit-border-radius: 150px; -moz-border-radius: 150px;">'''
    flash("you are now logged in as %s" % login_session['username'])
    return output


# Method for disconnecting from fabebook
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have been logged out.'

# This method enables login from Google.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parmeter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
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
    # Verify that the acces token is used for the intended user.
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
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += ''' " style = "width: 300px: height: 300px; border-radius:150px;
        -webkit-border-radius: 150px; -moz-border-radius: 150px;">'''
    flash("you are now logged in as %s" % login_session['username'])
    return output

# This method enables the user to disconect from Google or Facebook.
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']
        flash('You have successfully been logged out.')
        return redirect(url_for('showCategories'))
    else:
        flash('You were not logged in to begin with!')
        return redirect(url_for('showCategories'))

# Method for creating a new user.
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Method for getting user info.
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# Method for getting user ID.
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Method for disconnecting from google sign in.
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
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

# 9. Method to get JSON APIs of all categories
@app.route('/catalog.json')
def catalogsJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories],
        items=[i.serialize for i in items])

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
    categories = session.query(Category).order_by(Category.name)
    users = session.query(User).order_by(User.name).all()
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
    items = session.query(Item).filter_by(category_id=currentCategory.id)
    if 'username' not in login_session:
        return render_template('publicCategory.html', items=items,
            category=currentCategory.name, categories=categories)
    else:
        return render_template('category.html', items=items,
            category=currentCategory.name, categories=categories)


# 14. Method to create a new item.
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    categories = session.query(Category).order_by(Category.name)
    if 'username' not in login_session:
        return redirect('/login')
    # Indent this section after finishing the above section.
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

# 15. Method to show description & name of a certain itme.
@app.route('/catalog/<current_category>/<current_item>')
def showItem(current_category, current_item):
    category = session.query(Category).filter_by\
        (name = current_category.title()).one()
    item = session.query(Item).filter_by(name=current_item).one()
    if 'username' not in login_session:
        return render_template('publicItem.html', item=item)
    else:
        return render_template('item.html', item=item)

# 16. Method to edit an item name, description & category.
@app.route('/catalog/<current_item>/edit', methods=['GET', 'POST'])
def editItem(current_item):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(name=current_item).one()
    category = session.query(Category).filter_by\
        (id=editedItem.category_id).one()
    categories = session.query(Category).order_by(Category.name)
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

# 17. Method to delete an item.
@app.route('/catalog/<current_item>/delete', methods=['GET', 'POST'])
def deleteItem(current_item):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(name=current_item).one()
    category = session.query(Category).filter_by\
        (id=itemToDelete.category_id).one()
    categories = session.query(Category).order_by(Category.name)
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
