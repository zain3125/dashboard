from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

# بيانات وهمية لتجربة الواجهة
truck_owners_list = []
suppliers_list = []
factories_list = []
zones_list = []  # ✅ المناطق
representatives_list = []  # ✅ المندوبين

@app.route("/")
def index():
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/dashboard/data-entry")
def data_entry():
    return render_template("data_entry.html")

@app.route("/dashboard/dimension-tables")
def dimension_tables():
    return render_template("dimension_tables.html")

@app.route("/dashboard/transactions")
def transactions():
    return render_template("transactions.html")

@app.route("/dashboard/dimension-tables/add-truck-owner", methods=['GET', 'POST'])
def add_truck_owner():
    if request.method == 'POST':
        truck_number = request.form.get('truck_number')
        truck_owner = request.form.get('truck_owner')
        phone_number = request.form.get('phone_number')
        if truck_number and truck_owner:
            truck_owners_list.append({
                'truck_number': truck_number,
                'truck_owner': truck_owner,
                'phone_number': phone_number
            })
    return render_template("add_truck_owner.html", truck_owners=truck_owners_list)

@app.route("/dashboard/dimension-tables/add-supplier", methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        supplier_name = request.form.get('supplier_name')
        if supplier_name:
            suppliers_list.append(supplier_name)
    return render_template("add_supplier.html", suppliers=suppliers_list)

@app.route("/dashboard/dimension-tables/add-factory", methods=['GET', 'POST'])
def add_factory():
    if request.method == 'POST':
        factory_name = request.form.get('factory_name')
        if factory_name:
            factories_list.append(factory_name)
    return render_template("add_factory.html", factories=factories_list)

# ✅ صفحة Add Zone
@app.route("/dashboard/dimension-tables/add-zone", methods=['GET', 'POST'])
def add_zone():
    if request.method == 'POST':
        zone_name = request.form.get('zone_name')
        if zone_name:
            zones_list.append(zone_name)
    return render_template("add_zone.html", zones=zones_list)

# ✅ صفحة Add Representative
@app.route("/dashboard/dimension-tables/add-representative", methods=['GET', 'POST'])
def add_representative():
    if request.method == 'POST':
        rep_name = request.form.get('rep_name')
        rep_phone = request.form.get('rep_phone')
        if rep_name and rep_phone:
            representatives_list.append({
                'name': rep_name,
                'phone': rep_phone
            })
    return render_template("add_representative.html", representatives=representatives_list)

if __name__ == "__main__":
    app.run(debug=True)
