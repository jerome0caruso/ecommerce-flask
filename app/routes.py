from app import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import UserInfoForm, PostForm, LoginForm
from app.models import User, Post, Products


@app.route('/')
def index():
    product_1_info = {
        'name': "T-shirt",
        'price': 9.99,
        'description': "This is a blue shirt"
    }
    product_2_info = {
        'name': "Pants",
        'price': 19.99,
        'description': "This is yellow pants"
    }
    product_1 = Products("T-shirt", 9.99, "This is a blue shirt", current_user.id)
    product_2 = Products("Pants", 19.99, "This is yellow pants", current_user.id)
    product_3 = Products("T-shirt", 9.99, "This is a blue shirt", current_user.id)
    product_4 = Products("Pants", 19.99, "This is yellow pants", current_user.id)


    

    my_products = [product_1, product_2, product_3, product_4]

    for product in my_products:
        db.session.add(product)
        
    db.session.commit()
    return render_template('index.html', products=my_products )




@app.route('/signup', methods=["GET", 'POST'])
def signup():
    signup_form = UserInfoForm()
    if signup_form.validate_on_submit():
        # Grab Data from form
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data

        # Check if the username from the form already exists in the User table
        existing_user = User.query.filter_by(username=username).all()
        # If there is a user with that username message them asking them to try again
        if existing_user:
            # Flash a warning message
            flash(f'The username {username} is already registered. Please try again.', 'danger')
            # Redirect back to the register page
            return redirect(url_for('register'))

        # Create a new user instance
        new_user = User(username, email, password)
        # Add that user to the database
        db.session.add(new_user)
        db.session.commit()
        # Flash a success message thanking them for signing up
        flash(f'Thank you {username}, you have succesfully registered!', 'success')

        # Redirecting to the home page
        return redirect(url_for('index'))
        
    return render_template('signup.html', form=signup_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab data from form
        username = form.username.data
        password = form.password.data

        # Query our User table for a user with username
        user = User.query.filter_by(username=username).first()

        # Check if the user is None or if password is incorrect
        if user is None or not user.check_password(password):
            flash('Your username or password is incorrect', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)

        flash(f'Welcome {user.username}. You have succesfully logged in.', 'success')

        return redirect(url_for('index'))
        

    return render_template('login.html', login_form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/createpost', methods=['GET', 'POST'])
@login_required
def createpost():
    form = PostForm()
    if form.validate_on_submit():
        print('Hello')
        title = form.title.data
        content = form.content.data
        new_post = Post(title, content, current_user.id)
        db.session.add(new_post)
        db.session.commit()

        flash(f'The post {title} has been created.', 'primary')
        return redirect(url_for('index'))
        
    return render_template('createpost.html', form=form)


@app.route('/my-account')
@login_required
def my_account():
    return render_template('my_account.html')


@app.route('/my-posts')
@login_required
def my_posts():
    posts = current_user.posts
    return render_template('my_posts.html', posts=posts)

@app.route('/my_cart')
@login_required
def my_cart():
    # posts = current_user.posts
    return render_template('my_cart.html')

@app.route('/product_page/<int:product_id>')
@login_required
def product_page(product_id):
    product = Products.query.get_or_404(product_id)
    return render_template('product_page.html', product=product)


@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)


@app.route('/posts/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author.id != current_user.id:
        flash('That is not your post. You may only edit posts you have created.', 'danger')
        return redirect(url_for('my_posts'))
    form = PostForm()
    if form.validate_on_submit():
        new_title = form.title.data
        new_content = form.content.data
        print(new_title, new_content)
        post.title = new_title
        post.content = new_content
        db.session.commit()

        flash(f'{post.title} has been saved', 'success')
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('post_update.html', post=post, form=form)

@app.route('/product_page/<int:product_id>/cart', methods=['POST'])
@login_required
def add_cart(product_id):
    product = Post.query.get_or_404(product_id)
    # if post.author != current_user:
    #     flash('You can only delete your own posts', 'danger')
    #     return redirect(url_for('my_posts'))

    # db.session.delete(post)
    # db.session.commit()

    # flash(f'{post.title} has been deleted', 'success')
    return redirect(url_for('index'))



@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You can only delete your own posts', 'danger')
        return redirect(url_for('my_posts'))

    db.session.delete(post)
    db.session.commit()

    flash(f'{post.title} has been deleted', 'success')
    return redirect(url_for('my_posts'))