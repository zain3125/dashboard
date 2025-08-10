from flask import (
    render_template, request, redirect, url_for,
    send_file, flash, session, abort, jsonify
)
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from utils import (
    export_transactions_to_excel, fetch_transactions_from_db, insert_truck_owner,
    fetch_all_truck_owners, search_truck_owners, insert_supplier, fetch_all_suppliers,
    search_suppliers, insert_zone, fetch_all_zones, search_zones, insert_factory,
    fetch_all_factories, insert_representative, fetch_all_representatives,
    get_user_by_username, update_user_password, get_all_users, get_custody_by_user_id,
    fetch_all_trucks_with_owners, save_data_entry, update_naqla_record,
    get_current_month_records
)

# ========================
# Decorator to protect routes
# ========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("🔒 يجب تسجيل الدخول أولاً", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def register_routes(app):
    # ========================
    # Authentication routes
    # ========================
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"].strip()

            user = get_user_by_username(username)
            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                flash("✅ تم تسجيل الدخول بنجاح", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("❌ اسم المستخدم أو كلمة المرور غير صحيحة", "danger")

        return render_template("login.html")
    
    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("login"))

    # ========================
    # Dashboard & Data
    # ========================
    @app.route("/")
    def index():
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", username=session["username"], role=session["role"], user_id=session["user_id"])

    @app.route("/settings")
    @login_required
    def settings():
        return render_template("settings.html")

    @app.route("/data-entry", methods=["GET", "POST"])
    def data_entry():
        if request.method == "POST":
            # لو فيه naqla_id يبقى تعديل
            naqla_ids = request.form.getlist("naqla_id[]")
            
            if any(naqla_ids):
                # تعديل سجل واحد أو أكثر
                for i, naqla_id in enumerate(naqla_ids):
                    if naqla_id:  # تعديل
                        data = {
                            "date": request.form.getlist("date[]")[i],
                            "truck_num": request.form.getlist("truck_num[]")[i],
                            "truck_owner": request.form.getlist("truck_owner[]")[i],
                            "supplier": request.form.getlist("supplier[]")[i],
                            "factory": request.form.getlist("factory[]")[i],
                            "zone": request.form.getlist("zone[]")[i],
                            "weight": request.form.getlist("weight[]")[i],
                            "ohda": request.form.getlist("ohda[]")[i],
                            "factory_price": request.form.getlist("factory_price[]")[i],
                            "sell_price": request.form.getlist("sell_price[]")[i],
                            "representative": request.form.getlist("representative[]")[i]
                        }
                        update_naqla_record(naqla_id, data)
                    else:
                        # إضافة سجل جديد
                        data = {
                            "dates": [request.form.getlist("date[]")[i]],
                            "truck_nums": [request.form.getlist("truck_num[]")[i]],
                            "truck_owners": [request.form.getlist("truck_owner[]")[i]],
                            "suppliers": [request.form.getlist("supplier[]")[i]],
                            "factories_list": [request.form.getlist("factory[]")[i]],
                            "zones_list": [request.form.getlist("zone[]")[i]],
                            "weights": [request.form.getlist("weight[]")[i]],
                            "ohdas": [request.form.getlist("ohda[]")[i]],
                            "factory_prices": [request.form.getlist("factory_price[]")[i]],
                            "sell_prices": [request.form.getlist("sell_price[]")[i]],
                            "representatives_list": [request.form.getlist("representative[]")[i]]
                        }
                        save_data_entry(data)

                flash("✅ تم حفظ/تعديل البيانات بنجاح!", "success")
            else:
                # إدخال بيانات جديدة بالكامل
                data = {
                    "dates": request.form.getlist("date[]"),
                    "truck_nums": request.form.getlist("truck_num[]"),
                    "truck_owners": request.form.getlist("truck_owner[]"),
                    "suppliers": request.form.getlist("supplier[]"),
                    "factories_list": request.form.getlist("factory[]"),
                    "zones_list": request.form.getlist("zone[]"),
                    "weights": request.form.getlist("weight[]"),
                    "ohdas": request.form.getlist("ohda[]"),
                    "factory_prices": request.form.getlist("factory_price[]"),
                    "sell_prices": request.form.getlist("sell_price[]"),
                    "representatives_list": request.form.getlist("representative[]")
                }
                if save_data_entry(data):
                    flash("✅ تم حفظ البيانات بنجاح!", "success")
                else:
                    flash("❌ حدث خطأ أثناء حفظ البيانات", "error")

            return redirect(url_for("data_entry"))

        # عرض الصفحة مع جدول السجلات الحالية
        trucks = fetch_all_trucks_with_owners()
        suppliers, _ = fetch_all_suppliers(limit=100, offset=0)
        factories, _ = fetch_all_factories(page=1, per_page=100, query="")
        zones, _ = fetch_all_zones(limit=100, offset=0)
        representatives, _ = fetch_all_representatives(page=1, per_page=100)
        month_records = get_current_month_records()  # من utils

        return render_template(
            "data_entry.html",
            trucks=trucks,
            suppliers=suppliers,
            factories=factories,
            zones=zones,
            representatives=representatives,
            month_records=month_records
        )

    @app.route("/dashboard/dimension-tables")
    @login_required
    def dimension_tables():
        return render_template("dimension_tables.html")
    
    @app.route('/update_record', methods=['POST'])
    @login_required
    def update_record_route():
        """
        Handles the AJAX request to update a single record.
        This is a new, dedicated route for the edit/save functionality.
        """
        data = request.json
        naqla_id = data.get('id')
        if not naqla_id:
            return jsonify({'success': False, 'error': 'No ID provided'})
        
        # Call the corrected update function from utils.py
        response = update_naqla_record(naqla_id, data)
        return jsonify(response)


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
                truck_owner = request.form.get('truck_owner')
                phone_number = request.form.get('phone_number')

                if truck_number and truck_owner:
                    insert_truck_owner(truck_number, truck_owner, phone_number)
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
            return "حدث خطأ أثناء معالجة الطلب"

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
    @login_required
    def transactions():
        transactions_data = []
        start = end = ""
        page = int(request.args.get("page", 1))
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
    @login_required
    def export_transactions():
        start = request.form.get("start_date")
        end = request.form.get("end_date")
        file_path = export_transactions_to_excel(start, end)
        if file_path:
            return send_file(file_path, as_attachment=True)
        return "Export failed or no data found"

    @app.route("/change-password", methods=["GET", "POST"])
    @login_required
    def change_password():
        if request.method == "POST":
            current_password = request.form["current_password"].strip()
            new_password = request.form["new_password"].strip()
            confirm_password = request.form["confirm_password"].strip()

            # جلب بيانات المستخدم الحالي
            user = get_user_by_username(session["username"])

            # التحقق من كلمة المرور الحالية
            if not check_password_hash(user["password_hash"], current_password):
                flash("❌ كلمة المرور الحالية غير صحيحة", "danger")
                return redirect(url_for("change_password"))

            # التحقق من تطابق كلمة المرور الجديدة مع التأكيد
            if new_password != confirm_password:
                flash("❌ كلمة المرور الجديدة غير متطابقة", "danger")
                return redirect(url_for("change_password"))

            # تحديث كلمة المرور
            new_password_hash = generate_password_hash(new_password)
            update_user_password(user["id"], new_password_hash)

            flash("✅ تم تغيير كلمة المرور بنجاح", "success")
            return redirect(url_for("dashboard"))

        return render_template("change_password.html")

    @app.route("/custodies")
    def custodies():
        # لازم يكون المستخدم مسجل دخول
        if "user_id" not in session:
            return redirect(url_for("login"))

        role = session.get("role")

        # لو Admin أو Accountant يشوف كل العهد (ما عدا المحاسبين)
        if role in ["admin", "accountant"]:
            users = get_all_users(exclude_roles=["accountant", "admin"])
            return render_template("custodies_list.html", users=users)

        # لو موظف عادي → يروح مباشرة لعهدته
        return redirect(url_for("custody_detail", user_id=session["user_id"]))


    @app.route("/custody/<int:user_id>")
    def custody_detail(user_id):
        if "user_id" not in session:
            return redirect(url_for("login"))

        role = session.get("role")
        current_user_id = session["user_id"]

        # لو Admin أو Accountant → يقدر يشوف أي عهدة
        # لو موظف عادي → يقدر يشوف بس عهدته
        if role not in ["admin", "accountant"] and current_user_id != user_id:
            abort(403)  # ممنوع

        custody_data = get_custody_by_user_id(user_id)
        return render_template("custody_detail.html", custody_data=custody_data)
