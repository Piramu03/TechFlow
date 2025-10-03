from . import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    total_qty = db.Column(db.Integer, nullable=False, default=0)
    min_qty = db.Column(db.Integer, default=10)
    def __repr__(self):
        return f"<Product {self.name}>"

class Location(db.Model):
    __tablename__ = 'location'
    location_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Location {self.name}>"

class ProductMovement(db.Model):
    __tablename__ = 'productmovement'
    movement_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    from_location = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.Integer, db.ForeignKey('location.location_id'), nullable=True)
    qty = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='movements')
    from_loc = db.relationship('Location', foreign_keys=[from_location])
    to_loc = db.relationship('Location', foreign_keys=[to_location])

    def __repr__(self):
        return f"<Move {self.product_id} {self.qty}>"
