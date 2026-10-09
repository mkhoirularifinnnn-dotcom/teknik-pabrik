from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models.barang import Barang, TransaksiGudang

barang_bp = Blueprint('barang', __name__)

@barang_bp.route('/barang', methods=['GET', 'POST'])
@login_required
def daftar_barang():
    if current_user.role != 'Pengadaan':
        flash('Hanya bagian Pengadaan yang dapat mengelola master data barang.', 'danger')
        return redirect(url_for('auth.redirect_dashboard'))
        
    if request.method == 'POST':
        nama_barang = request.form.get('nama_barang')
        satuan = request.form.get('satuan')
        stok_awal = request.form.get('stok')
        
        # Simpan master barang baru
        new_barang = Barang(
            nama_barang=nama_barang,
            satuan=satuan,
            stok=int(stok_awal) if stok_awal else 0
        )
        db.session.add(new_barang)
        db.session.commit()
        
        # Catat transaksi stok awal masuk gudang
        if int(stok_awal) > 0:
            transaksi = TransaksiGudang(
                barang_id=new_barang.id,
                jenis_transaksi='MASUK',
                jumlah=int(stok_awal),
                keterangan='Stok awal master data barang'
            )
            db.session.add(transaksi)
            db.session.commit()
        
        flash('Master data barang berhasil ditambahkan!', 'success')
        return redirect(url_for('barang.daftar_barang'))
        
    barang_list = Barang.query.all()
    return render_template('barang/daftar_barang.html', barang_list=barang_list)