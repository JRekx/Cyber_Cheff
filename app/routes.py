from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from model import User
from forms import LoginForm, RegistrationForm
import requests
from urllib.parse import unquote

main = Blueprint('main', __name__)

# Your Spoonacular API key
API_KEY = '15599c84fad84a0f9a160bc14e9ea4d6'

@main.route('/home', methods=['GET'])
def home():
    # The home route which renders the main page
    return render_template('index.html', recipes=[], search_query='')

@main.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already authenticated, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user instance
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        # Add new user to the database
        db.session.add(user)
        db.session.commit()
        # Redirect to the login page after successful registration
        return redirect(url_for('main.login'))

    # Render the registration template
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already authenticated, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        # Query the database for the user
        user = User.query.filter_by(email=form.email.data).first()
        # Validate password and log the user in
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))

    # Render the login template
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    # Logout the current user
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/profile')
@login_required
def profile():
    # Render the profile page of the current user
    return render_template('profile.html', user=current_user)

@main.route('/', methods=['GET', 'POST'])
def index():
    # Main index route to handle recipe searches
    if request.method == 'POST':
        # Handle the form submission
        query = request.form.get('search_query', '')
        recipes = search_recipes(query)
        return render_template('index.html', recipes=recipes, search_query=query)

    search_query = request.args.get('search_query', '')
    decoded_search_query = unquote(search_query)
    recipes = search_recipes(decoded_search_query)
    return render_template('index.html', recipes=recipes, search_query=decoded_search_query)

def search_recipes(query):
    # Function to search for recipes based on the provided query
    url = f'https://api.spoonacular.com/recipes/complexSearch'
    params = {
        'apiKey': API_KEY,
        'query': query,
        'number': 10,
        'instructionsRequired': True,
        'addRecipeInformation': True,
        'fillIngredients': True,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    return []

@main.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    # Route to view a specific recipe
    search_query = request.args.get('search_query', '')
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {'apiKey': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        recipe = response.json()
        return render_template('view_recipe.html', recipe=recipe, search_query=search_query)
    return "Recipe not found", 404

@login_manager.user_loader
def load_user(user_id):
    # User loader callback for Flask-Login
    return User.query.get(int(user_id))
