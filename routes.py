from flask import render_template, request, redirect, url_for, send_file, flash
from utils import (
    export_transactions_to_excel, fetch_transactions_from_db, insert_truck_owner,
    fetch_all_truck_owners, search_truck_owners, insert_supplier, fetch_all_suppliers,
    search_suppliers, insert_zone, fetch_all_zones, search_zones, insert_factory,
    fetch_all_factories, insert_representative, fetch_all_representatives
)

representatives_list = []

def register_routes(app):
    @app.route("/")
    def index():
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/dashboard/data-entry")
    def data_entry():
        return render_template("data_entry.html")

    @app.route("/dashboard/dimension-tables")
    def dimension_tables():
        return render_template("dimension_tables.html")

        # 🚚 Truck Owners
    @app.route("/dashboard/dimension-tables/add-truck-owner", methods=['GET', 'POST'])
    def add_truck_owner():
        try:
            page = int(request.args.get("page", 1))
            limit = 10
            offset = (page - 1) * limit
            query = request.args.get("query", "").strip()

            if request.method == 'POST':
                truck_number = request.form.get('truck_number')
                truck_owner = request.form.get('truck_owner')
                phone_number = request.form.get('phone_number')

                if truck_number and truck_owner:
                    try:
                        insert_truck_owner(truck_number, truck_owner, phone_number)
                        flash("✅ تم إضافة مالك الشاحنة بنجاح", "success")
                    except Exception as e:
                        flash(f"❌ فشل في الإضافة: {str(e)}", "error")
                    return redirect(url_for("add_truck_owner", page=page))

            if query:
                truck_owners = search_truck_owners(query)
                total_pages = 1
            else:
                truck_owners, total_count = fetch_all_truck_owners(limit=limit, offset=offset)
                total_pages = (total_count + limit - 1) // limit

            return render_template("add_truck_owner.html",
                                truck_owners=truck_owners,
                                page=page,
                                total_pages=total_pages)
        except Exception as e:
            print(f"Error in add_truck_owner: {e}")
            flash("حدث خطأ أثناء معالجة الطلب", "error")
            return redirect(url_for("add_truck_owner", page=1))


    # 🏭 Factories
    @app.route("/dashboard/dimension-tables/add-factory", methods=['GET', 'POST'])
    def add_factory():
        PER_PAGE = 10
        query = request.args.get("query", "").strip()
        page = int(request.args.get("page", 1))

        if request.method == 'POST':
            factory_name = request.form.get('factory_name', '').strip()
            if not factory_name:
                flash("❌ أدخل اسم المصنع", "error")
                return redirect(url_for('add_factory'))

            result = insert_factory(factory_name)
            if result == "inserted":
                flash("✅ تم إضافة المصنع بنجاح", "success")
            elif result == "exists":
                flash("⚠️ المصنع موجود بالفعل", "warning")
            else:
                flash("❌ حدث خطأ أثناء إضافة المصنع", "error")

            return redirect(url_for('add_factory', page=page))

        factories, total_pages = fetch_all_factories(page, PER_PAGE, query)
        return render_template("add_factory.html", factories=factories, page=page, total_pages=total_pages)

    @app.route("/dashboard/dimension-tables/add-supplier", methods=['GET', 'POST'])
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
                    insert_supplier(supplier_name, phone_number)
                    return redirect(url_for("add_supplier", page=page))

            if query:
                suppliers = search_suppliers(query)
                total_pages = 1
            else:
                suppliers, total_count = fetch_all_suppliers(limit=limit, offset=offset)
                total_pages = (total_count + limit - 1) // limit

            return render_template("add_supplier.html",
                                suppliers=suppliers,
                                page=page,
                                total_pages=total_pages)
        except Exception as e:
            print(f"Error in add_supplier: {e}")
            return "حدث خطأ أثناء معالجة الطلب"

    # 📍 Zones
    @app.route("/dashboard/dimension-tables/add-zone", methods=['GET', 'POST'])
    def add_zone():
        try:
            page = int(request.args.get("page", 1))
            limit = 10
            offset = (page - 1) * limit
            query = request.args.get("query", "").strip()

            if request.method == 'POST':
                zone_name = request.form.get('zone_name')
                if zone_name:
                    result = insert_zone(zone_name)
                    if result is True:
                        flash("✅ تم إضافة المنطقة بنجاح", "success")
                    elif result is False:
                        flash("⚠️ اسم المنطقة موجود بالفعل", "warning")
                    else:
                        flash("❌ حدث خطأ أثناء الإضافة", "error")
                    return redirect(url_for("add_zone", page=page))

            if query:
                zones = search_zones(query)
                total_pages = 1
            else:
                zones, total_count = fetch_all_zones(limit=limit, offset=offset)
                total_pages = (total_count + limit - 1) // limit

            return render_template("add_zone.html", zones=zones, page=page, total_pages=total_pages)
        except Exception as e:
            print(f"Error in add_zone: {e}")
            flash("❌ حدث خطأ أثناء معالجة الطلب", "error")
            return "حدث خطأ أثناء معالجة الطلب"

    @app.route("/dashboard/dimension-tables/add-representative", methods=['GET', 'POST'])
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

            result = insert_representative(representative_name, phone)
            if result == "inserted":
                flash("✅ تم إضافة المندوب بنجاح", "success")
            elif result == "exists":
                flash("⚠️ المندوب موجود بالفعل", "warning")
            else:
                flash("❌ حدث خطأ أثناء إضافة المندوب", "error")

            return redirect(url_for('add_representative', page=page))

        representatives, total_pages = fetch_all_representatives(page, PER_PAGE, query)
        return render_template("add_representative.html", representatives=representatives, page=page, total_pages=total_pages)



    # 💰 Transactions
    @app.route("/dashboard/transactions", methods=['GET', 'POST'])
    def transactions():
        transactions_data = []
        start = end = ""
        page = int(request.args.get("page", 1))  # ← رقم الصفحة
        per_page = 10
        offset = (page - 1) * per_page

        if request.method == 'POST':
            start = request.form.get("start_date")
            end = request.form.get("end_date")
            transactions_data = fetch_transactions_from_db(start, end, limit=per_page, offset=offset)
        elif request.method == 'GET':
            start = request.args.get("start_date", "")
            end = request.args.get("end_date", "")
            if start and end:
                transactions_data = fetch_transactions_from_db(start, end, limit=per_page, offset=offset)

        return render_template(
            "transactions.html",
            transactions=transactions_data,
            start=start,
            end=end,
            page=page
        )

    # ⬇️ Export Excel
    @app.route("/dashboard/transactions/export", methods=['POST'])
    def export_transactions():
        start = request.form.get("start_date")
        end = request.form.get("end_date")
        file_path = export_transactions_to_excel(start, end)
        if file_path:
            return send_file(file_path, as_attachment=True)
        return "Export failed or no data found"
