from app import create_app, db
from app.models import Product, Location, ProductMovement

app = create_app()

# Create DB tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
