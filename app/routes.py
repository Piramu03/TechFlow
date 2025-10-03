from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Product, Location, ProductMovement
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.products'))

# ---------- PRODUCTS ----------
@main.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        total_qty = int(request.form.get('total_qty') or 0)
        if not name:
            flash("Product name required", "error")
        else:
            p = Product(name=name, total_qty=total_qty)
            db.session.add(p)
            db.session.commit()
            flash("Product added", "success")
        return redirect(url_for('main.products'))

    items = Product.query.order_by(Product.name).all()
    return render_template('products.html', products=items)

@main.route('/products/edit/<int:id>', methods=['GET','POST'])
def edit_product(id):
    p = Product.query.get_or_404(id)
    if request.method == 'POST':
        p.name = request.form.get('name').strip()
        p.total_qty = int(request.form.get('total_qty') or 0)
        db.session.commit()
        flash("Product updated", "success")
        return redirect(url_for('main.products'))
    return render_template('edit_product.html', product=p)

@main.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    p = Product.query.get_or_404(id)
    # optional: prevent delete if movements exist
    db.session.delete(p)
    db.session.commit()
    flash("Product deleted", "success")
    return redirect(url_for('main.products'))

# ---------- LOCATIONS ----------
@main.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        if not name:
            flash("Location name required", "error")
        else:
            l = Location(name=name)
            db.session.add(l)
            db.session.commit()
            flash("Location added", "success")
        return redirect(url_for('main.locations'))
    locs = Location.query.order_by(Location.name).all()
    return render_template('locations.html', locations=locs)

@main.route('/locations/edit/<int:id>', methods=['GET','POST'])
def edit_location(id):
    loc = Location.query.get_or_404(id)
    if request.method == 'POST':
        loc.name = request.form.get('name').strip()
        db.session.commit()
        flash("Location updated", "success")
        return redirect(url_for('main.locations'))
    return render_template('edit_location.html', location=loc)

@main.route('/locations/delete/<int:id>', methods=['POST'])
def delete_location(id):
    loc = Location.query.get_or_404(id)
    db.session.delete(loc)
    db.session.commit()
    flash("Location deleted", "success")
    return redirect(url_for('main.locations'))

# ---------- MOVEMENTS ----------
@main.route('/movements', methods=['GET', 'POST'])
def movements():
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()

    if request.method == 'POST':
        product_id = int(request.form.get('product_id'))
        from_loc = request.form.get('from_location') or None
        to_loc = request.form.get('to_location') or None
        # store integers or None
        from_loc = int(from_loc) if from_loc else None
        to_loc = int(to_loc) if to_loc else None
        qty = int(request.form.get('qty') or 0)

        product = Product.query.get_or_404(product_id)

        # compute current remaining by summing all movements
        total_moved = db.session.query(db.func.sum(ProductMovement.qty)).filter(
            ProductMovement.product_id == product_id
        ).scalar() or 0
        remaining = product.total_qty - total_moved

        # If this movement is an OUT (from_location present) ensure remaining >= qty
        if from_loc and qty > remaining:
            flash(f"Cannot move {qty}. Only {remaining} available.", "error")
            moves = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
            return render_template('movements.html', movements=moves, products=products, locations=locations)

        move = ProductMovement(
            product_id=product_id,
            from_location=from_loc,
            to_location=to_loc,
            qty=qty,
            timestamp=datetime.utcnow()
        )
        db.session.add(move)
        db.session.commit()
        flash("Movement added", "success")
        return redirect(url_for('main.movements'))

    moves = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', movements=moves, products=products, locations=locations)

@main.route('/movements/edit/<int:id>', methods=['GET','POST'])
def edit_movement(id):
    move = ProductMovement.query.get_or_404(id)
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()
    if request.method == 'POST':
        move.product_id = int(request.form.get('product_id'))
        from_loc = request.form.get('from_location') or None
        to_loc = request.form.get('to_location') or None
        move.from_location = int(from_loc) if from_loc else None
        move.to_location = int(to_loc) if to_loc else None
        move.qty = int(request.form.get('qty') or 0)
        db.session.commit()
        flash("Movement updated", "success")
        return redirect(url_for('main.movements'))
    return render_template('edit_movement.html', movement=move, products=products, locations=locations)

@main.route('/delete_movement/<int:id>', methods=['POST'])
def delete_movement(id):
    move = ProductMovement.query.get_or_404(id)
    db.session.delete(move)
    db.session.commit()
    flash("Movement deleted", "success")
    return redirect(url_for('main.movements'))

# ---------- REPORT: movement history with remaining stock progressive ----------
@main.route('/report')
def report():
    movements = ProductMovement.query.order_by(ProductMovement.timestamp.asc()).all()

    # init balances per product from Product.total_qty
    balances = {p.product_id: p.total_qty for p in Product.query.all()}

    report_data = []
    for m in movements:
        product = Product.query.get(m.product_id)
        from_name = m.from_loc.name if m.from_loc else "N/A"
        to_name = m.to_loc.name if m.to_loc else "N/A"
        route = f"{from_name} → {to_name}"

        # If movement is an outgoing (from_location present) reduce balance
        if m.from_location:
            balances[m.product_id] -= m.qty

        # If movement is incoming (to_location present) increase balance
        if m.to_location and not m.from_location:
            # incoming where stock enters system (from_location None)
            # or explicit transfer with to_location present (handled above for from)
            # here we add in case both from and to present and we want to account to_location too
            # but for transfers we already decreased from source; adding to dest handled when iterating movements
            balances[m.product_id] += 0  # no-op: we handle transfers by a single record (decrement source)
            # NOTE: our convention: one movement row represents both sides (decrement source, increment dest)
            # If you record incoming as from_location None and to_location set, you should instead
            # treat that as increase. We'll handle both types below more simply

        # Simpler handling (more correct): recompute progressive balances by applying effects to both locations:
        # but since we only keep a per-product global balance (total across all locations), we do: if from_location -> -qty, if to_location and from_location is None -> +qty
        # For clarity: (incoming rows have from_location None)
        # If from_location is None and to_location present -> add qty
        if m.from_location is None and m.to_location is not None:
            balances[m.product_id] += m.qty

        remaining = balances[m.product_id]

        report_data.append({
            'id': m.movement_id,
            'total_qty': product.total_qty,
            'product': product.name,
            'route': route,
            'delivered': m.qty,
            'remaining': remaining,
            'timestamp': m.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    # Show newest first in UI if you prefer:
    report_data.reverse()  # optional: newest first
    return render_template('report.html', report_data=report_data)

# ---------- BALANCE GRID: Product x Location ----------
@main.route('/balance')
def balance():
    # build list of (product, location, qty) where qty > 0
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()

    grid = []
    for p in products:
        for loc in locations:
            # sum of movements TO this location for this product
            in_qty = db.session.query(db.func.sum(ProductMovement.qty)).filter(
                ProductMovement.product_id == p.product_id,
                ProductMovement.to_location == loc.location_id
            ).scalar() or 0
            # sum of movements FROM this location for this product
            out_qty = db.session.query(db.func.sum(ProductMovement.qty)).filter(
                ProductMovement.product_id == p.product_id,
                ProductMovement.from_location == loc.location_id
            ).scalar() or 0
            qty = in_qty - out_qty
            if qty != 0:
                grid.append({'product': p, 'location': loc, 'qty': qty})
    return render_template('balance.html', grid=grid)
