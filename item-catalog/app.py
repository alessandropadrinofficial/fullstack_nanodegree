#!/usr/bin/env python3
import string
import random
import json
from functools import wraps
from flask import Flask, render_template, request, redirect
from flask import url_for, jsonify
from flask import session as login_session
from flask import make_response
from catalog_db import Category, Item, User
from catalog_db import session
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


# Create an instance of the class Flask
# with the name of the running app as the argument '__name__'
app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authenticaltion - check if user is logged-in
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            return "You are not allowed to access there"

            return redirect('/login')
    return decorated_function


# Json with credentials
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "buttonsignin"


def create_user(login_session):
    """ User helper functions
        Creates a new user in our db
    """
    new_user = User(name=login_session['username'],
                    email=login_session['email'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    """ Returns user object assoccieted with id number,
        if user id passed into the method
    """
    user = session.query(User).filter_by(id=user_id).one_or_none()
    return user


def get_user_id(email):
    """ Takes an email and reterns an id, if email belongs to a user
        stored inour db
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# Google login
def google_connect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print("HERE***************")
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='',
                                             redirect_uri='postmessage')
        # oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
    url = url.format(access_token)
    # Create Get request containing the URL and access token

    result = requests.get(url).json()

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']

    # Check if user exists, if it doesn't create a new one
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    # Response thet knows user's name and return their pictura
    html = """
        <h1>Welcome, {name}!</h1>
        <img src="{picture}" style = "width: 300px;
            height: 300px; border-radius: 150px;
            -webkit-border-radius: 150px;-moz-border-radius: 150px;">
    """.format(name=login_session['username'],
               picture=login_session['picture'])

    return html


# DISCONNECT - Revoke a current user's token and reset their login_session
def google_disconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])

    # Revoke access token
    result = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': login_session['access_token']},
                           headers={'content-type':
                                    'application/x-www-form-urlencoded'})

    print('result is ')
    print(result)

    # Reset users session since otherwise it won't be possible to
    # logout and login
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    if result.status_code == 200:
        # Reset the user's session
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        message = json.dumps('Failed to revoke token for given user.')
        response = make_response(message, 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Create a state token to prevent request forgery
# Store it in the session for later validation
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # Render the login template
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connects to google account"""
    return google_connect()


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnects from google account"""
    return google_disconnect()


# Root
@app.route('/catalog/')
@app.route('/')
def show_catalog():
    """Show all catalog categories and items
    """

    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('catalog.html', categories=categories, items=items)


# JSON endpoint
@app.route('/catalog.json')
def catalog_json():
    """Return list of categories and items in each category
    """

    categories = session.query(Category).all()
    catalog = []

    # iterate over categories and format them
    for c in categories:
        items = session.query(Item).filter_by(category_id=c.id)
        c = c.serialize
        c['Item'] = [i.serialize for i in items]

        catalog.append(c)

    return jsonify(Category=catalog)


@app.route('/catalog/<category_name>/<item_name>.json')
def item_json(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(category_id=category.id,
                                         name=item_name).one()
    result = {}
    result['Item'] = item.serialize
    return jsonify(result)


# Show category with items
@app.route('/catalog/<category_name>/items/')
def show_category(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id)
    categories = session.query(Category).all()
    return render_template('catalog.html', items=items, categories=categories)


# Show description
@app.route('/catalog/<category_name>/<item_name>/')
def show_item_description(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(name=item_name,
                                         category_id=category.id).one()
    return render_template('item_page.html', item=item)


# Edit an item
@app.route('/catalog/<category_name>/<item_name>/edit',
           methods=['GET', 'POST'])
@login_required
def edit_item(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    edited_item = session.query(Item).filter_by(name=item_name,
                                                category_id=category.id).one()

    # Authorisation - check if current user can edit the item
    # Only a user who created an item can edit/delete it
    user_id = get_user_id(login_session['email'])
    if edited_item.user_id != user_id:
        message = json.dumps('You are not allowed to edit the item')
        response = make_response(message, 403)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Post method
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['description']:
            edited_item.description = request.form['description']
        if request.form['category']:
            category = session.query(Category).filter_by(name=request.form
                                                         ['category']).one()
            edited_item.category = category

        session.add(edited_item)
        session.commit()
        return redirect(url_for('show_category',
                                category_name=edited_item.category.name))
    else:
        categories = session.query(Category).all()
        return render_template('edit_page.html', item=edited_item,
                               categories=categories)


# Delete item
@app.route('/catalog/<category_name>/<item_name>/delete',
           methods=['GET', 'POST'])
@login_required
def delete_item(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item_to_delete = session.query(Item).filter_by(name=item_name,
                                                   category=category).one()

    # Authorisation - check if current user can edit the item
    # Only a user who created an item can edit/delete it
    user_id = get_user_id(login_session['email'])
    if item_to_delete.user_id != user_id:
        message = json.dumps('You are not allowed to delete the item')
        response = make_response(message, 403)
        response.headers['Content-Type'] = 'application/json'
        return response

    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        return redirect(url_for('show_category',
                                category_name=category.name))

    else:
        return render_template('delete_page.html', item=item_to_delete)


# Add an item
@app.route('/catalog/add', methods=['GET', 'POST'])
@login_required
def add_item():
    categories = session.query(Category).all()
    if request.method == 'POST':
        new_item = Item(
            name=request.form['name'],
            description=request.form['description'],
            category=session.query(Category).
            filter_by(name=request.form['category']).one(),
            user_id=login_session['user_id'])

        session.add(new_item)
        session.commit()

        return redirect(url_for('show_catalog'))
    else:
        return render_template('add_page.html', categories=categories)


if __name__ == '__main__':
    app.secret_key = 'Super Secret Key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
