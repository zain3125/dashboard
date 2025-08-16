# main_routes.py
from flask import (
    render_template, request, redirect, url_for,
    flash, session, jsonify
)
from .auth_routes import login_required
from services.main_data_manager import save_data_entry, update_naqla_record, get_current_month_records, delete_naqla_record
from services.table_managers import TruckOwnerManager, SupplierManager, ZoneManager, FactoryManager, RepresentativeManager

# ========================
# Class Instances
# ========================
truck_owner_manager = TruckOwnerManager()
supplier_manager = SupplierManager()
zone_manager = ZoneManager()
factory_manager = FactoryManager()
representative_manager = RepresentativeManager()

def register_main_routes(app):
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
            delete_id = request.form.get("delete_id")
            if delete_id:
                result = delete_naqla_record(delete_id)
                if result['success']:
                    flash("🗑️ تم حذف السجل بنجاح!", "success")
                else:
                    flash(f"❌ فشل الحذف: {result['error']}", "error")
                return redirect(url_for("data_entry"))
            naqla_ids = request.form.getlist("naqla_id[]")
            if any(naqla_ids):
                for i, naqla_id in enumerate(naqla_ids):
                    if naqla_id:
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

        trucks = truck_owner_manager.fetch_trucks_with_owners()
        suppliers, _ = supplier_manager.fetch_all(limit=100, offset=0)
        factories, _ = factory_manager.fetch_all(page=1, per_page=100, query="")
        zones, _ = zone_manager.fetch_all_records(limit=100, offset=0)
        representatives, _ = representative_manager.fetch_all(limit=10, offset=1)
        month_records = get_current_month_records()

        return render_template(
            "data_entry.html",
            trucks=trucks,
            suppliers=suppliers,
            factories=factories,
            zones=zones,
            representatives=representatives,
            month_records=month_records
        )

    @app.route('/update_record', methods=['POST'])
    @login_required
    def update_record_route():
        data = request.json
        naqla_id = data.get('id')
        if not naqla_id:
            return jsonify({'success': False, 'error': 'No ID provided'})
        response = update_naqla_record(naqla_id, data)
        return jsonify(response)