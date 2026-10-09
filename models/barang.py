from extensions import db
from datetime import datetime

class Barang(db.Model):
    __tablename__ = 'barang'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_barang = db.Column(db.String(100), nullable=False)
    stok = db.Column(db.Integer, default=0)
    satuan = db.Column(db.String(20), nullable=False)
    gudang_pabrik = db.Column(db.String(50), nullable=False, default='Sedep')

    kebutuhan_laporan = db.relationship('KebutuhanBarang', back_populates='barang', lazy=True)
    transaksi = db.relationship('TransaksiGudang', backref='barang', lazy=True, cascade='all, delete-orphan')


class KebutuhanBarang(db.Model):
    __tablename__ = 'kebutuhan_barang'
    
    id = db.Column(db.Integer, primary_key=True)
    laporan_id = db.Column(db.Integer, db.ForeignKey('laporan_kerusakan.id'), nullable=False)
    barang_id = db.Column(db.Integer, db.ForeignKey('barang.id'), nullable=False)
    jumlah_diminta = db.Column(db.Integer, nullable=False)
    status_pengadaan = db.Column(db.String(50), default='MENUNGGU PERSETUJUAN')
    
    laporan = db.relationship('LaporanKerusakan', back_populates='kebutuhan_list')
    barang = db.relationship('Barang', back_populates='kebutuhan_laporan')


class TransaksiGudang(db.Model):
    __tablename__ = 'transaksi_gudang'
    
    id = db.Column(db.Integer, primary_key=True)
    barang_id = db.Column(db.Integer, db.ForeignKey('barang.id'), nullable=False)
    jenis_transaksi = db.Column(db.String(20), nullable=False) # MASUK / KELUAR
    jumlah = db.Column(db.Integer, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    keterangan = db.Column(db.Text, nullable=True)