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

