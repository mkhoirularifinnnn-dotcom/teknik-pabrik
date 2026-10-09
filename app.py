from flask import Flask, redirect, url_for
from flask_login import LoginManager
from extensions import db
from models.user import User
from models.mesin import Mesin
from models.barang import Barang, KebutuhanBarang, TransaksiGudang
from models.laporan import LaporanKerusakan, PemeriksaanKerusakan

# Import Blueprints
from routes.auth import auth_bp
from routes.mesin import mesin_bp
from routes.barang import barang_bp
from routes.laporan import laporan_bp
from routes.pengadaan import pengadaan_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci-rahasia-teknik-pabrik-sedep'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teknik_pabrik.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi Ekstensi
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registrasi Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(mesin_bp)
app.register_blueprint(barang_bp)
app.register_blueprint(laporan_bp)
app.register_blueprint(pengadaan_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

def create_default_users():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='astek1').first():
            from werkzeug.security import generate_password_hash
            users_data = [
                ('maskep1', generate_password_hash('password123'), 'MASKep'),
                ('astek1', generate_password_hash('password123'), 'ASTEK'),
                ('pengadaan1', generate_password_hash('password123'), 'Pengadaan'),
                ('asisten1', generate_password_hash('password123'), 'Asisten Pengolahan')
            ]
            for uname, pwd, role in users_data:
                new_user = User(username=uname, password=pwd, role=role)
                db.session.add(new_user)
            db.session.commit()

if __name__ == '__main__':
    create_default_users()
    app.run(debug=True, port=5000)