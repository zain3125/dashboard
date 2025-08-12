# dimension_routes.py
from flask import (
    render_template, request, redirect, url_for,
    flash, jsonify
)
from .auth_routes import login_required
from services.table_managers import TruckOwnerManager, SupplierManager, ZoneManager, FactoryManager, RepresentativeManager

# ========================
# Class Instances
# ========================
truck_owner_manager = TruckOwnerManager()
supplier_manager = SupplierManager()
zone_manager = ZoneManager()
factory_manager = FactoryManager()
representative_manager = RepresentativeManager()

def register_dimension_routes(app):
    @app.route("/dashboard/dimension-tables")
    @login_required
    def dimension_tables():
        return render_template("dimension_tables.html")
    
    # 🚚 Truck Owners
    @app.route("/dashboard/dimension-tables/add-truck-owner", methods=['GET', 'POST'])
    @login_required
    def add_truck_owner():
        try:
            page = int(request.args.get("page", 1))
            limit = 10
            offset = (page - 1) * limit
            query = request.args.get("query", "").strip()
            if request.method == 'POST':
                truck_number = request.form.get('truck_number')
                truck_owner_name = request.form.get('truck_owner')
                phone_number = request.form.get('phone_number')
                if truck_number and truck_owner_name:
                    response = truck_owner_manager.insert_record(truck_number, truck_owner_name, phone_number)
                    if response.get('success'):
                        flash("✅ تم إضافة مالك الشاحنة بنجاح", "success")
                    else:
                        flash(f"❌ حدث خطأ: {response.get('error', 'غير معروف')}", "error")
                    return redirect(url_for("add_truck_owner", page=page))
            if query:
                truck_owners = truck_owner_manager.search(query)
                total_pages = 1
            else:
                truck_owners, total_count = truck_owner_manager.fetch_all(limit=limit, offset=offset)
                total_pages = (total_count + limit - 1) // limit
            return render_template("add_truck_owner.html",
                                   truck_owners=truck_owners,
                                   page=page,
                                   total_pages=total_pages)
        except Exception as e:
            flash("❌ حدث خطأ أثناء معالجة الطلب", "error")
            return redirect(url_for("add_truck_owner"))

    @app.route('/update_truck_owner', methods=['POST'])
    @login_required
    def update_truck_owner_route():
        data = request.json
        original_truck_num = data.get('id')
        new_data = {
            'new_truck_num': data.get('truck_num'),
            'new_owner_name': data.get('owner_name'),
            'new_phone': data.get('phone')
        }
        if not original_truck_num:
            return jsonify({'success': False, 'error': 'No original truck number provided'})
        response = truck_owner_manager.update_record(original_truck_num, new_data)
        return jsonify(response)

    # 🏭 Factories
    @app.route("/dashboard/dimension-tables/add-factory", methods=['GET', 'POST'])
    @login_required
    def add_factory():
        PER_PAGE = 10
        query = request.args.get("query", "").strip()
        page = int(request.args.get("page", 1))
        if request.method == 'POST':
            factory_name = request.form.get('factory_name', '').strip()
            if not factory_name:
                flash("❌ أدخل اسم المصنع", "error")
                return redirect(url_for('add_factory'))
            result = factory_manager.insert_record(factory_name)
            if result == "inserted":
                flash("✅ تم إضافة المصنع بنجاح", "success")
            elif result == "exists":
                flash("⚠️ المصنع موجود بالفعل", "warning")
            else:
                flash("❌ حدث خطأ أثناء إضافة المصنع", "error")
            return redirect(url_for('add_factory', page=page))
        factories, total_pages = factory_manager.fetch_all(page, PER_PAGE, query)
        return render_template("add_factory.html", factories=factories, page=page, total_pages=total_pages)

    # 📦 Suppliers
    @app.route("/dashboard/dimension-tables/add-supplier", methods=['GET', 'POST'])
    @login_required
    def add_supplier():
        try:
            page = int(request.args.get("page", 1))
            limit = 10
            offset = (page - 1) * limit
            query = request.args.get("query", "").strip()
            if request.method == 'POST':
                supplier_name = request.form.get('supplier_name')
                phone_number = request.form.get('phone_number')
                if supplier_name and phone_number:
                    if supplier_manager.insert_record(supplier_name, phone_number):
                        flash("✅ تم إضافة المورد بنجاح", "success")
                    else:
                        flash("❌ حدث خطأ أثناء إضافة المورد", "error")
                    return redirect(url_for("add_supplier", page=page))
            if query:
                suppliers = supplier_manager.search(query)
                total_pages = 1
            else:
                suppliers, total_count = supplier_manager.fetch_all(limit=limit, offset=offset)
                total_pages = (total_count + limit - 1) // limit
            return render_template("add_supplier.html",
                                   suppliers=suppliers,
                                   page=page,
                                   total_pages=total_pages)
        except Exception as e:
            flash("❌ حدث خطأ أثناء معالجة الطلب", "error")
            return redirect(url_for("add_supplier"))

    # 📍 Zones
    @app.route("/dashboard/dimension-tables/add-zone", methods=['GET', 'POST'])
    @login_required
    def add_zone():
        try:
            page = int(request.args.get("page", 1))
            limit = 10
            offset = (page - 1) * limit
            query = request.args.get("query", "").strip()
            if request.method == 'POST':
                zone_name = request.form.get('zone_name')
                if zone_name:
                    result = zone_manager.insert_record(zone_name)
                    if result is True:
                        flash("✅ تم إضافة المنطقة بنجاح", "success")
                    elif result is False:
                        flash("⚠️ اسم المنطقة موجود بالفعل", "warning")
                    else:
                        flash("❌ حدث خطأ أثناء الإضافة", "error")
                    return redirect(url_for("add_zone", page=page))
            if query:
                zones = zone_manager.search_records(query)
                total_pages = 1
            else:
                zones, total_count = zone_manager.fetch_all_records(limit=limit, offset=offset)
                total_pages = (total_count + limit - 1) // limit
            return render_template("add_zone.html", zones=zones, page=page, total_pages=total_pages)
        except Exception as e:
            flash("❌ حدث خطأ أثناء معالجة الطلب", "error")
            return redirect(url_for("add_zone"))

    # 👨‍💼 Representatives
    @app.route("/dashboard/dimension-tables/add-representative", methods=['GET', 'POST'])
    @login_required
    def add_representative():
        PER_PAGE = 10
        query = request.args.get("query", "").strip()
        page = int(request.args.get("page", 1))
        if request.method == 'POST':
            representative_name = request.form.get('representative_name', '').strip()
            phone = request.form.get('phone', '').strip()
            if not representative_name or not phone:
                flash("❌ أدخل اسم ورقم المندوب", "error")
                return redirect(url_for('add_representative', page=page))
            result = representative_manager.insert_record(representative_name, phone)
            if result == "inserted":
                flash("✅ تم إضافة المندوب بنجاح", "success")
            elif result == "exists":
                flash("⚠️ المندوب موجود بالفعل", "warning")
            else:
                flash("❌ حدث خطأ أثناء إضافة المندوب", "error")
            return redirect(url_for('add_representative', page=page))
        representatives, total_pages = representative_manager.fetch_all(page, PER_PAGE, query)
        return render_template("add_representative.html", representatives=representatives, page=page, total_pages=total_pages)