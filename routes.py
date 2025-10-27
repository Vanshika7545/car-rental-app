from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from app import app, db
from models import User, Car, CarModel, Rental
from forms import LoginForm, RegistrationForm, CarForm, CarModelForm, SearchForm, RentalForm

# Home page
@app.route('/')
def home():
    # Get featured car models (limit to 6)
    featured_models = CarModel.query.filter_by(is_available=True).limit(6).all()
    return render_template('home.html', featured_models=featured_models)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            # Redirect to appropriate dashboard based on role
            if user.is_admin:
                return redirect(next_page or url_for('admin_dashboard'))
            else:
                return redirect(next_page or url_for('user_dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
    cars = Car.query.all()
    car_models = CarModel.query.all()
    active_rentals = Rental.query.filter_by(status='active').all()
    
    stats = {
        'total_cars': len(cars),
        'total_models': len(car_models),
        'active_rentals': len(active_rentals)
    }
    
    return render_template('admin/dashboard.html', stats=stats, cars=cars, car_models=car_models, active_rentals=active_rentals)

@app.route('/admin/car/add', methods=['GET', 'POST'])
@login_required
def add_car():
    if not current_user.is_admin:
        abort(403)
    
    form = CarForm()
    if form.validate_on_submit():
        car = Car(
            brand=form.brand.data,
            year=form.year.data,
            description=form.description.data
        )
        db.session.add(car)
        db.session.commit()
        flash('Car has been added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_car.html', form=form)

@app.route('/admin/car/<int:car_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    if not current_user.is_admin:
        abort(403)
    
    car = Car.query.get_or_404(car_id)
    form = CarForm()
    
    if form.validate_on_submit():
        car.brand = form.brand.data
        car.year = form.year.data
        car.description = form.description.data
        car.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Car has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    elif request.method == 'GET':
        form.brand.data = car.brand
        form.year.data = car.year
        form.description.data = car.description
    
    return render_template('admin/edit_car.html', form=form, car=car)

@app.route('/admin/car/<int:car_id>/delete', methods=['POST'])
@login_required
def delete_car(car_id):
    if not current_user.is_admin:
        abort(403)
    
    car = Car.query.get_or_404(car_id)
    
    # Check if any car models are being rented
    models_with_rentals = False
    for model in car.models:
        if Rental.query.filter_by(car_model_id=model.id, status='active').first():
            models_with_rentals = True
            break
    
    if models_with_rentals:
        flash('Cannot delete car. One or more models are currently being rented.', 'danger')
    else:
        db.session.delete(car)
        db.session.commit()
        flash('Car has been deleted!', 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/car_model/add', methods=['GET', 'POST'])
@login_required
def add_car_model():
    if not current_user.is_admin:
        abort(403)
    
    form = CarModelForm()
    # Get all cars for the car_id select field
    form.car_id.choices = [(car.id, f"{car.brand} ({car.year})") for car in Car.query.all()]
    
    if form.validate_on_submit():
        car_model = CarModel(
            car_id=form.car_id.data,
            name=form.name.data,
            price_per_day=form.price_per_day.data,
            mileage=form.mileage.data,
            fuel_type=form.fuel_type.data,
            transmission=form.transmission.data,
            seats=form.seats.data,
            air_conditioning=form.air_conditioning.data,
            image_url=form.image_url.data
        )
        db.session.add(car_model)
        db.session.commit()
        flash('Car model has been added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_car_model.html', form=form)

@app.route('/admin/car_model/<int:model_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_car_model(model_id):
    if not current_user.is_admin:
        abort(403)
    
    car_model = CarModel.query.get_or_404(model_id)
    form = CarModelForm()
    
    # Get all cars for the car_id select field
    form.car_id.choices = [(car.id, f"{car.brand} ({car.year})") for car in Car.query.all()]
    
    if form.validate_on_submit():
        car_model.car_id = form.car_id.data
        car_model.name = form.name.data
        car_model.price_per_day = form.price_per_day.data
        car_model.mileage = form.mileage.data
        car_model.fuel_type = form.fuel_type.data
        car_model.transmission = form.transmission.data
        car_model.seats = form.seats.data
        car_model.air_conditioning = form.air_conditioning.data
        car_model.image_url = form.image_url.data
        car_model.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Car model has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    elif request.method == 'GET':
        form.car_id.data = car_model.car_id
        form.name.data = car_model.name
        form.price_per_day.data = car_model.price_per_day
        form.mileage.data = car_model.mileage
        form.fuel_type.data = car_model.fuel_type
        form.transmission.data = car_model.transmission
        form.seats.data = car_model.seats
        form.air_conditioning.data = car_model.air_conditioning
        form.image_url.data = car_model.image_url
    
    return render_template('admin/edit_car_model.html', form=form, car_model=car_model)

@app.route('/admin/car_model/<int:model_id>/delete', methods=['POST'])
@login_required
def delete_car_model(model_id):
    if not current_user.is_admin:
        abort(403)
    
    car_model = CarModel.query.get_or_404(model_id)
    
    # Check if the car model is being rented
    active_rental = Rental.query.filter_by(car_model_id=model_id, status='active').first()
    if active_rental:
        flash('Cannot delete car model. It is currently being rented.', 'danger')
    else:
        db.session.delete(car_model)
        db.session.commit()
        flash('Car model has been deleted!', 'success')
    
    return redirect(url_for('admin_dashboard'))

# User routes
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    car_models = CarModel.query.filter_by(is_available=True).all()
    
    # Get car brands for filtering
    brands = db.session.query(Car.brand).distinct().all()
    brands = [brand[0] for brand in brands]
    
    # Search form
    form = SearchForm()
    
    return render_template('user/dashboard.html', car_models=car_models, brands=brands, form=form)

@app.route('/user/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    
    if form.validate_on_submit() or request.args.get('query'):
        query = form.query.data or request.args.get('query')
        
        # Search cars and car models
        car_results = Car.query.filter(or_(
            Car.brand.ilike(f'%{query}%'),
            Car.description.ilike(f'%{query}%')
        )).all()
        
        car_ids = [car.id for car in car_results]
        
        # Find car models related to the cars or matching the query directly
        model_results = CarModel.query.filter(or_(
            CarModel.car_id.in_(car_ids),
            CarModel.name.ilike(f'%{query}%'),
            CarModel.fuel_type.ilike(f'%{query}%'),
            CarModel.transmission.ilike(f'%{query}%')
        )).all()
        
        # Get car brands for filtering
        brands = db.session.query(Car.brand).distinct().all()
        brands = [brand[0] for brand in brands]
        
        return render_template('user/dashboard.html', 
                               car_models=model_results, 
                               search_query=query, 
                               brands=brands, 
                               form=form)
    
    return redirect(url_for('user_dashboard'))

@app.route('/user/car/<int:model_id>', methods=['GET', 'POST'])
@login_required
def car_details(model_id):
    car_model = CarModel.query.get_or_404(model_id)
    form = RentalForm()
    
    if form.validate_on_submit():
        # Calculate number of days and total price
        start_date = form.start_date.data
        end_date = form.end_date.data
        days = (end_date - start_date).days + 1
        total_price = days * car_model.price_per_day
        
        # Check if the car model is available for the requested period
        conflicting_rentals = Rental.query.filter(
            Rental.car_model_id == model_id,
            Rental.status == 'active',
            or_(
                # Check if rental period overlaps with existing rentals
                (Rental.start_date <= start_date) & (Rental.end_date >= start_date),
                (Rental.start_date <= end_date) & (Rental.end_date >= end_date),
                (Rental.start_date >= start_date) & (Rental.end_date <= end_date)
            )
        ).all()
        
        if conflicting_rentals:
            flash('This car is already booked for the selected dates. Please choose different dates.', 'danger')
        else:
            rental = Rental(
                user_id=current_user.id,
                car_model_id=car_model.id,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                status='active'
            )
            db.session.add(rental)
            car_model.is_available = False
            db.session.commit()
            flash('Car rental confirmed successfully!', 'success')
            return redirect(url_for('my_rentals'))
    
    form.car_model_id.data = car_model.id
    today = datetime.today().date()
    
    return render_template('user/car_details.html', car_model=car_model, form=form, today=today)

@app.route('/user/my_rentals')
@login_required
def my_rentals():
    rentals = Rental.query.filter_by(user_id=current_user.id).order_by(Rental.created_at.desc()).all()
    return render_template('user/my_rentals.html', rentals=rentals)

@app.route('/user/rentals/<int:rental_id>/cancel', methods=['POST'])
@login_required
def cancel_rental(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    
    # Ensure the rental belongs to the current user
    if rental.user_id != current_user.id:
        abort(403)
    
    # Only allow cancellation of pending or active rentals
    if rental.status in ['pending', 'active']:
        rental.status = 'cancelled'
        
        # Make the car model available again
        car_model = CarModel.query.get(rental.car_model_id)
        car_model.is_available = True
        
        db.session.commit()
        flash('Rental has been cancelled successfully!', 'success')
    else:
        flash('Cannot cancel this rental.', 'danger')
    
    return redirect(url_for('my_rentals'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
