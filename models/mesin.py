from extensions import db

class Mesin(db.Model):
    __tablename__ = 'mesin'
    
    id = db.Column(db.Integer, primary_key=True)
    kode_mesin = db.Column(db.String(50), unique=True, nullable=False)
    nama_mesin = db.Column(db.String(150), nullable=False)
    lokasi = db.Column(db.String(150), nullable=False)
    status_operasional = db.Column(db.String(50), default='Normal') # Normal, Rusak, Maintenance
    
    def __repr__(self):
        return f'<Mesin {self.nama_mesin} ({self.lokasi})>'