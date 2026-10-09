from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from models.barang import KebutuhanBarang

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/asisten')
@login_required
def asisten_dashboard():
    # Validasi role ketat di backend
    if current_user.role != 'Asisten Pengolahan':
        abort(403) # Forbidden / Akses Ditolak
    return render_template('dashboard/asisten.html', user=current_user)

@dashboard_bp.route('/dashboard/astek')
@login_required
def astek_dashboard():
    if current_user.role != 'ASTEK':
        abort(403)
    return render_template('dashboard/astek.html', user=current_user)

@dashboard_bp.route('/dashboard/pengadaan')
@login_required
def pengadaan_dashboard():
    if current_user.role != 'Pengadaan':
        abort(403)
    
    # Ambil data kebutuhan barang agar tabel pengadaan terisi dengan benar
    kebutuhan_list = KebutuhanBarang.query.all()
    return render_template('pengadaan/daftar_pengadaan.html', kebutuhan_list=kebutuhan_list, user=current_user)

@dashboard_bp.route('/dashboard/maskep')
@login_required
def maskep_dashboard():
    if current_user.role != 'MASKep':
        abort(403)
    return render_template('dashboard/maskep.html', user=current_user)