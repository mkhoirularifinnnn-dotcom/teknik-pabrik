from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models.barang import Barang, TransaksiGudang, KebutuhanBarang

pengadaan_bp = Blueprint('pengadaan', __name__)

@pengadaan_bp.route('/pengadaan/barang', methods=['GET'])
@login_required
def daftar_barang():
    if current_user.role != 'Pengadaan':
        flash('Anda tidak memiliki izin mengakses halaman pengadaan.', 'danger')
        return redirect(url_for('auth.redirect_dashboard'))
        
    gudang_aktif = request.args.get('gudang', 'Sedep')
    barang_list = Barang.query.filter_by(gudang_pabrik=gudang_aktif).all()
    daftar_gudang = ['Sedep', 'Arumsari', 'Talun', 'Santosa', 'Purbasari']
    
    pengajuan_list = KebutuhanBarang.query.join(Barang).filter(
        Barang.gudang_pabrik == gudang_aktif,
        KebutuhanBarang.status_pengadaan == 'MENUNGGU PERSETUJUAN'
    ).all()
    
    return render_template('pengadaan/daftar_barang.html', 
                           barang_list=barang_list, 
                           pengajuan_list=pengajuan_list,
                           gudang_aktif=gudang_aktif, 
                           daftar_gudang=daftar_gudang)

@pengadaan_bp.route('/pengadaan/persetujuan/<int:kebutuhan_id>/<aksi>', methods=['POST'])
@login_required
def proses_persetujuan(kebutuhan_id, aksi):
    if current_user.role != 'Pengadaan':
        flash('Anda tidak memiliki izin.', 'danger')
        return redirect(url_for('auth.redirect_dashboard'))
        
    kebutuhan = KebutuhanBarang.query.get_or_404(kebutuhan_id)
    barang = kebutuhan.barang
    gudang_pabrik = barang.gudang_pabrik
    
    if aksi == 'setujui':
        if barang.stok >= kebutuhan.jumlah_diminta:
            barang.stok -= kebutuhan.jumlah_diminta
            kebutuhan.status_pengadaan = 'DISETUJUI (STOK DIPOTONG)'
            
            transaksi_keluar = TransaksiGudang(
                barang_id=barang.id,
                jenis_transaksi='KELUAR',
                jumlah=kebutuhan.jumlah_diminta,
                keterangan=f"Disetujui untuk Laporan Perbaikan No. {kebutuhan.laporan.nomor_laporan}"
            )
            db.session.add(transaksi_keluar)
            db.session.commit()
            flash(f'Pengajuan {barang.nama_barang} sebanyak {kebutuhan.jumlah_diminta} disetujui. Stok Gudang {gudang_pabrik} otomatis berkurang!', 'success')
        else:
            flash(f'Stok di Gudang {gudang_pabrik} tidak mencukupi (sisa stok: {barang.stok})!', 'danger')
            
    elif aksi == 'tolak':
        kebutuhan.status_pengadaan = 'DITOLAK'
        db.session.commit()
        flash('Pengajuan permintaan barang ditolak.', 'warning')
        
    return redirect(url_for('pengadaan.daftar_barang', gudang=gudang_pabrik))

@pengadaan_bp.route('/pengadaan/barang/tambah', methods=['GET', 'POST'])
@login_required
def tambah_barang():
    if current_user.role != 'Pengadaan':
        flash('Anda tidak memiliki izin.', 'danger')
        return redirect(url_for('auth.redirect_dashboard'))
        
    gudang_param = request.args.get('gudang', 'Sedep')
    
    if request.method == 'POST':
        nama_barang = request.form.get('nama_barang')
        stok = int(request.form.get('stok', 0))
        satuan = request.form.get('satuan')
        gudang_pabrik = request.form.get('gudang_pabrik', gudang_param)
        
        if nama_barang and satuan and gudang_pabrik:
            new_barang = Barang(
                nama_barang=nama_barang,
                stok=stok,
                satuan=satuan,
                gudang_pabrik=gudang_pabrik
            )
            db.session.add(new_barang)
            db.session.flush()
            
            if stok > 0:
                transaksi = TransaksiGudang(
                    barang_id=new_barang.id,
                    jenis_transaksi='MASUK',
                    jumlah=stok,
                    keterangan='Stok awal gudang'
                )
                db.session.add(transaksi)
                
            db.session.commit()
            flash(f'Barang berhasil ditambahkan ke Gudang Pabrik {gudang_pabrik}!', 'success')
            return redirect(url_for('pengadaan.daftar_barang', gudang=gudang_pabrik))
            
    return render_template('pengadaan/tambah_barang.html', gudang_param=gudang_param)

@pengadaan_bp.route('/pengadaan/barang/tambah-stok/<int:barang_id>', methods=['POST'])
@login_required
def tambah_stok(barang_id):
    if current_user.role != 'Pengadaan':
        flash('Anda tidak memiliki izin.', 'danger')
        return redirect(url_for('auth.redirect_dashboard'))
        
    barang = Barang.query.get_or_404(barang_id)
    jumlah_tambah = int(request.form.get('jumlah_tambah', 0))
    
    if jumlah_tambah > 0:
        barang.stok += jumlah_tambah
        
        transaksi = TransaksiGudang(
            barang_id=barang.id,
            jenis_transaksi='MASUK',
            jumlah=jumlah_tambah,
            keterangan='Penambahan/Pengadaan stok baru'
        )
        db.session.add(transaksi)
        db.session.commit()
        flash(f'Stok barang {barang.nama_barang} di Gudang {barang.gudang_pabrik} berhasil ditambah!', 'success')
        
    return redirect(url_for('pengadaan.daftar_barang', gudang=barang.gudang_pabrik))