@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Валидация на бэкенде
        errors = []

        if len(username) < 3:
            errors.append('Имя пользователя должно содержать минимум 3 символа.')
        if User.query.filter_by(username=username).first():
            errors.append('Это имя пользователя уже занято.')
        if not email:
            errors.append('Email обязателен.')
        elif User.query.filter_by(email=email).first():
            errors.append('Этот email уже зарегистрирован.')
        if len(password) < 6:
            errors.append('Пароль должен содержать минимум 6 символов.')
        if password != confirm_password:
            errors.append('Пароли не совпадают.')

        if errors:
            for error in errors:
                flash(error)
            return render_template('register.html')

        # Создание пользователя
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Вы успешно вошли в систему!')
            return redirect(url_for('my_trips'))
        else:
            flash('Неверное имя пользователя или пароль.')

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Вы вышли из системы.')
    return redirect(url_for('index'))
import os
from werkzeug.utils import secure_filename


@app.route('/add_trip', methods=['GET', 'POST'])
def add_trip():
    if 'user_id' not in session:
        flash('Для добавления путешествия необходимо войти в систему.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description']
        cost = request.form.get('cost')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # Обработка изображения
        image_file = request.files.get('image')
        image_filename = None

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        # Создание записи о путешествии
        trip = Trip(
            title=title,
            description=description,
            user_id=session['user_id'],
            cost=float(cost) if cost else None,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            image_filename=image_filename
        )
        db.session.add(trip)
        db.session.commit()

        flash('Путешествие успешно добавлено!')
        return redirect(url_for('my_trips'))

    return render_template('add_trip.html')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
@app.route('/my_trips')
def my_trips():
    if 'user_id' not in session:
        flash('Для просмотра путешествий необходимо войти в систему.')
        return redirect(url_for('login'))

    trips = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.created_at.desc()).all()
    return render_template('my_trips.html', trips=trips)
@app.route('/edit_trip/<int:trip_id>', methods=['GET', 'POST'])
def edit_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        flash('У вас нет прав для редактирования этого путешествия.')
        return redirect(url_for('my_trips'))

    if request.method == 'POST':
        trip.title = request.form['title'].strip()
        trip.description = request.form['description']
        trip.cost = float(request.form['cost']) if request.form.get('cost') else None

        # Обработка нового изображения
        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            # Удаляем старое фото, если оно есть
            if trip.image_filename:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], trip.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            # Сохраняем новое фото
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            trip.image_filename = filename

        db.session.commit()
        flash('Путешествие успешно обновлено!')
        return redirect(url_for('my_trips'))

    return render_template('edit_trip.html', trip=trip)
@app.route('/delete_trip/<int:trip_id>')
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        flash('У вас нет прав для удаления этого путешествия.')
    else:
        # Удаляем файл изображения, если он есть
        if trip.image_filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], trip.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(trip)
        db.session.commit()
        flash('Путешествие удалено.')
    return redirect(url_for('my_trips'))
@app.route('/all_trips')
def all_trips():
    # Получаем все путешествия, сортируем по дате создания (новые сверху)
    trips = Trip.query.order_by(Trip.created_at.desc()).all()
    return render_template('all_trips.html', trips=trips)
