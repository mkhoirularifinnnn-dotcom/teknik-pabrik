from extensions import db

class LaporanKerusakan(db.Model):
    __tablename__ = 'laporan_kerusakan'
    
    id = db.Column(db.Integer, primary_key=True)
    nomor_laporan = db.Column(db.String(50), unique=True, nullable=False)
    mesin_id = db.Column(db.Integer, db.ForeignKey('mesin.id'), nullable=False)
    tanggal_laporan = db.Column(db.Date, nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    foto_bukti = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='PENDING') # PENDING, PROSES, SELESAI
    
    # Kolom Tanggal Tindak Lanjut (TL)
    rencana_tanggal = db.Column(db.Date, nullable=True)
    tanggal_realisasi = db.Column(db.Date, nullable=True)
    dokumentasi_realisasi = db.Column(db.Text, nullable=True)
    
    mesin = db.relationship('Mesin', backref=db.backref('laporan_kerusakan', lazy=True))
    kebutuhan_list = db.relationship('KebutuhanBarang', back_populates='laporan', lazy=True, cascade='all, delete-orphan')


class PemeriksaanKerusakan(db.Model):
    __tablename__ = 'pemeriksaan_kerusakan'
    
    id = db.Column(db.Integer, primary_key=True)
    laporan_id = db.Column(db.Integer, db.ForeignKey('laporan_kerusakan.id'), nullable=False)
    catatan = db.Column(db.Text, nullable=True)
    
    laporan = db.relationship('LaporanKerusakan', backref=db.backref('pemeriksaan', lazy=True, cascade='all, delete-orphan'))