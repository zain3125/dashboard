# main_routes.py
from flask import (
    render_template, request, redirect, url_for,
    flash, session, jsonify
)
from .auth_routes import login_required
from services.main_data_manager import save_data_entry, update_naqla_record, get_current_month_records, delete_naqla_record
from services.table_managers import TruckOwnerManager, SupplierManager, ZoneManager, FactoryManager, RepresentativeManager

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
            all_dates = request.form.getlist("date[]")
            all_truck_nums = request.form.getlist("truck_num[]")
            all_truck_owners = request.form.getlist("truck_owner[]")
            all_suppliers = request.form.getlist("supplier[]")
            all_factories = request.form.getlist("factory[]")
            all_zones = request.form.getlist("zone[]")
            all_weights = request.form.getlist("weight[]")
            all_ohdas = request.form.getlist("ohda[]")
            all_factory_prices = request.form.getlist("factory_price[]")
            all_sell_prices = request.form.getlist("sell_price[]")
            all_representatives = request.form.getlist("representative[]")
            new_records_to_save = []

            for i in range(len(all_dates)):
                record_data = {
                    "date": all_dates[i] if i < len(all_dates) else None,
                    "truck_num": all_truck_nums[i] if i < len(all_truck_nums) else None,
                    "truck_owner": all_truck_owners[i] if i < len(all_truck_owners) else None,
                    "supplier": all_suppliers[i] if i < len(all_suppliers) else None,
                    "factory": all_factories[i] if i < len(all_factories) else None,
                    "zone": all_zones[i] if i < len(all_zones) else None,
                    "weight": all_weights[i] if i < len(all_weights) else None,
                    "ohda": all_ohdas[i] if i < len(all_ohdas) else None,
                    "factory_price": all_factory_prices[i] if i < len(all_factory_prices) else None,
                    "sell_price": all_sell_prices[i] if i < len(all_sell_prices) else None,
                    "representative": all_representatives[i] if i < len(all_representatives) else None,
                }
                
                naqla_id = naqla_ids[i] if i < len(naqla_ids) else None
                if naqla_id:
                    update_naqla_record(naqla_id, record_data)
                elif record_data["date"] and record_data["truck_num"]:
                    new_records_to_save.append(record_data)

            if new_records_to_save:
                if save_data_entry(new_records_to_save):
                    flash("✅ تم حفظ البيانات بنجاح!", "success")
                else:
                    flash("❌ حدث خطأ أثناء حفظ البيانات", "error")
            return redirect(url_for("data_entry"))

        trucks = truck_owner_manager.fetch_trucks_with_owners()
        suppliers, _ = supplier_manager.fetch_all(limit=100, offset=0)
        factories, _ = factory_manager.fetch_all(limit=10, offset=1)
        zones, _ = zone_manager.fetch_all(limit=100, offset=0)
        representatives, _ = representative_manager.fetch_all(limit=100, offset=0)
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