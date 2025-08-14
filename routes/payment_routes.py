from flask import render_template, request, redirect, url_for, flash, jsonify
from services.payment_services import (
    get_supplier_payments, add_supplier_payment,
    get_truck_owner_payments, add_truck_owner_payment,
    update_supplier_payment, delete_supplier_payment,
    update_truck_owner_payment, delete_truck_owner_payment
)
from services.table_managers import SupplierManager, TruckOwnerManager

# إنشاء مدراء الجداول
supplier_manager = SupplierManager()
truck_owner_manager = TruckOwnerManager()


def register_payment_routes(app):
    @app.route("/payment")
    def payment():
        return render_template("payment.html")

    # دفع للموردين
    @app.route("/payment/supplier", methods=["GET", "POST"])
    def supplier_payment():
        if request.method == "POST":
            date_id = request.form.get("date_id", "").replace('-', '')
            supplier_id_str = request.form.get("supplier_id")  # يجب أن يتطابق هذا الاسم مع HTML

            if not supplier_id_str:
                flash("يجب اختيار مورد قبل إضافة الدفعة.", "danger")
                return redirect(url_for("supplier_payment"))

            try:
                supplier_id = int(supplier_id_str)
                amount = float(request.form.get("amount") or 0)
                transfer_fees = float(request.form.get("transfer_fees") or 0)
                payment_method = request.form.get("payment_method")
                notes = request.form.get("notes")
            except (ValueError, KeyError) as e:
                flash(f"خطأ في إدخال البيانات: {str(e)}. تأكد من إدخال قيم صحيحة.", "danger")
                return redirect(url_for("supplier_payment"))

            try:
                add_supplier_payment(
                    date_id,
                    supplier_id,
                    amount,
                    transfer_fees,
                    payment_method,
                    notes
                )
                flash("تمت إضافة دفعة للمورد بنجاح.", "success")
            except Exception as e:
                flash(f"حدث خطأ أثناء إضافة الدفعة: {str(e)}", "danger")

            return redirect(url_for("supplier_payment"))

        # جلب المدفوعات
        payments = get_supplier_payments(request.args.get("query"))
        # جلب قائمة الموردين
        suppliers, _ = supplier_manager.fetch_all(limit=1000, offset=0)

        return render_template("supplier_payment.html", payments=payments, suppliers=suppliers)

    # دفع لمالكي الشاحنات
    @app.route("/payment/truck-owner", methods=["GET", "POST"])
    def truck_owner_payment():
        if request.method == "POST":
            date_id = request.form.get("date_id", "").replace('-', '')
            owner_id_str = request.form.get("owner_id")

            if not owner_id_str:
                flash("يجب اختيار مالك شاحنة قبل إضافة الدفعة.", "danger")
                return redirect(url_for("truck_owner_payment"))

            try:
                owner_id = int(owner_id_str)
                amount = float(request.form.get("amount") or 0)
                transfer_fees = float(request.form.get("transfer_fees") or 0)
                payment_method = request.form.get("payment_method")
                notes = request.form.get("notes")
            except (ValueError, KeyError) as e:
                flash(f"خطأ في إدخال البيانات: {str(e)}. تأكد من إدخال قيم صحيحة.", "danger")
                return redirect(url_for("truck_owner_payment"))

            try:
                add_truck_owner_payment(
                    date_id,
                    owner_id,
                    amount,
                    transfer_fees,
                    payment_method,
                    notes
                )
                flash("تمت إضافة دفعة لمالك الشاحنة بنجاح.", "success")
            except Exception as e:
                flash(f"حدث خطأ أثناء إضافة الدفعة: {str(e)}", "danger")

            return redirect(url_for("truck_owner_payment"))

        # جلب المدفوعات
        payments = get_truck_owner_payments(request.args.get("query"))
        # جلب قائمة مالكي الشاحنات
        owners, _ = truck_owner_manager.fetch_all(limit=1000, offset=0)

        return render_template("truck_owner_payment.html", payments=payments, owners=owners)

    # تحديث دفعة مورد
    @app.route("/update_supplier_payment", methods=["POST"])
    def update_supplier_payment_route():
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        try:
            update_supplier_payment(
                data["id"],
                data["amount"],
                data.get("transfer_fees"),
                data.get("payment_method"),
                data.get("notes")
            )
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # حذف دفعة مورد
    @app.route("/delete_supplier_payment", methods=["POST"])
    def delete_supplier_payment_route():
        data = request.get_json()
        if not data or "id" not in data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        try:
            delete_supplier_payment(data["id"])
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # تحديث دفعة مالك الشاحنة
    @app.route("/update_truck_owner_payment", methods=["POST"])
    def update_truck_owner_payment_route():
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        try:
            update_truck_owner_payment(
                data["id"],
                data["amount"],
                data.get("transfer_fees"),
                data.get("payment_method"),
                data.get("notes")
            )
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # حذف دفعة مالك الشاحنة
    @app.route("/delete_truck_owner_payment", methods=["POST"])
    def delete_truck_owner_payment_route():
        data = request.get_json()
        if not data or "id" not in data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        try:
            delete_truck_owner_payment(data["id"])
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500