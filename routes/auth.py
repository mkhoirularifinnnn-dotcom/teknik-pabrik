from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Jika sudah login, langsung arahkan ke dashboard masing-masing role
    if current_user.is_authenticated:
        return redirect(url_for('auth.redirect_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Selamat datang kembali, {user.username}!', 'success')
            return redirect(url_for('auth.redirect_dashboard'))
        else:
            flash('Username atau Password salah. Silakan coba lagi.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/dashboard-redirect')
@login_required
def redirect_dashboard():
    # Validasi RBAC: Mengarahkan pengguna sesuai rolenya masing-masing
    if current_user.role == 'Asisten Pengolahan':
        return redirect(url_for('dashboard.asisten_dashboard'))
    elif current_user.role == 'ASTEK':
        return redirect(url_for('dashboard.astek_dashboard'))
    elif current_user.role == 'Pengadaan':
        return redirect(url_for('dashboard.pengadaan_dashboard'))
    elif current_user.role == 'MASKep':
        return redirect(url_for('dashboard.maskep_dashboard'))
    else:
        flash('Role pengguna tidak dikenali.', 'danger')
        return redirect(url_for('auth.logout'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil keluar sistem.', 'info')
    return redirect(url_for('auth.login'))