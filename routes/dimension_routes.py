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

    @app.route('/delete_truck_owner', methods=['POST'])
    @login_required
    def delete_truck_owner_route():
        data = request.json
        truck_num = data.get('truck_num')
        if not truck_num:
            return jsonify({'success': False, 'error': 'No truck number provided'})
        response = truck_owner_manager.delete_record(truck_num)
        return jsonify(response)

    # 📦 Suppliers Routes
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

    @app.route('/update_supplier', methods=['POST'])
    @login_required
    def update_supplier_route():
        data = request.json
        original_supplier_name = data.get('id')
        new_data = {
            'new_supplier_name': data.get('supplier_name'),
            'new_phone': data.get('phone')
        }
        if not original_supplier_name:
            return jsonify({'success': False, 'error': 'No original supplier name provided'})
        response = supplier_manager.update_record(original_supplier_name, new_data)
        return jsonify(response)
    
    @app.route('/delete_supplier', methods=['POST'])
    @login_required
    def delete_supplier_route():
        data = request.json
        supplier_name = data.get('supplier_name')
        if not supplier_name:
            return jsonify({'success': False, 'error': 'No supplier name provided'})
        
        response = supplier_manager.delete_record(supplier_name)
        return jsonify(response)

    # 🏭 Factory Routes
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

    @app.route('/update_factory', methods=['POST'])
    @login_required
    def update_factory_route():
        data = request.json
        original_factory_name = data.get('id')
        new_factory_name = data.get('factory_name')
        if not original_factory_name:
            return jsonify({'success': False, 'error': 'No original factory name provided'})
        
        response = factory_manager.update_record(original_factory_name, {'new_factory_name': new_factory_name})
        return jsonify(response)
    
    @app.route('/delete_factory', methods=['POST'])
    @login_required
    def delete_factory_route():
        data = request.json
        factory_name = data.get('factory_name')
        if not factory_name:
            return jsonify({'success': False, 'error': 'No factory name provided'})
        
        response = factory_manager.delete_record(factory_name)
        return jsonify(response)

    # 📍 Zone Routes
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

    @app.route('/update_zone', methods=['POST'])
    @login_required
    def update_zone_route():
        data = request.json
        original_zone_name = data.get('id')
        new_zone_name = data.get('zone_name')
        if not original_zone_name:
            return jsonify({'success': False, 'error': 'No original zone name provided'})
        
        response = zone_manager.update_record(original_zone_name, {'new_zone_name': new_zone_name})
        return jsonify(response)
    
    @app.route('/delete_zone', methods=['POST'])
    @login_required
    def delete_zone_route():
        data = request.json
        zone_name = data.get('zone_name')
        if not zone_name:
            return jsonify({'success': False, 'error': 'No zone name provided'})
        
        response = zone_manager.delete_record(zone_name)
        return jsonify(response)


    @app.route("/dashboard/dimension-tables/add-representative", methods=['GET', 'POST'])
    @login_required
    def add_representative():
        try:
            page = int(request.args.get("page", 1))
            limit = 10
            offset = (page - 1) * limit
            query = request.args.get("query", "").strip()

            if request.method == 'POST':
                representative_name = request.form.get('representative_name', '').strip()
                phone = request.form.get('phone', '').strip()

                if not representative_name or not phone:
                    flash("❌ أدخل اسم ورقم المندوب", "error")
                else:
                    result = representative_manager.insert_record(representative_name, phone)
                    if result == "inserted":
                        flash("✅ تم إضافة المندوب بنجاح", "success")
                    elif result == "exists":
                        flash("⚠️ المندوب موجود بالفعل", "warning")
                    else:
                        flash("❌ حدث خطأ أثناء إضافة المندوب", "error")
                
                return redirect(url_for('add_representative', page=page))

            # -------------------
            # منطق جلب البيانات والبحث
            if query:
                # عند البحث، لا تحتاج إلى تقسيم النتائج إلى صفحات
                # دالة search تعيد قائمة واحدة فقط
                representatives = representative_manager.search(query)
                total_count = len(representatives) # احسب العدد الإجمالي من القائمة
                total_pages = 1
            else:
                representatives, total_count = representative_manager.fetch_all(limit=limit, offset=offset)
                total_pages = (total_count + limit - 1) // limit
            # -------------------

            return render_template("add_representative.html",
                                representatives=representatives,
                                page=page,
                                total_pages=total_pages,
                                )
        except Exception as e:
            print(f"Error in add_representative route: {e}")
            flash("❌ حدث خطأ أثناء معالجة الطلب", "error")
            return redirect(url_for("add_representative"))

    # في مسار update_representative_route()
    @app.route('/update_representative', methods=['POST'])
    @login_required
    def update_representative_route():
        try:
            data = request.json
            original_representative_name = data.get('original_representative_name')
            
            new_data = {
                'new_representative_name': data.get('new_representative_name'),
                'new_phone': data.get('phone')
            }

            if not original_representative_name:
                return jsonify({'success': False, 'error': 'No original representative name provided'})


            response = representative_manager.update_record(original_representative_name, new_data)
            
            return jsonify(response)

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/delete_representative', methods=['POST'])
    @login_required
    def delete_representative_route():
        try:
            data = request.json
            representative_name = data.get('representative_name')
            if not representative_name:
                return jsonify({'success': False, 'error': 'No representative name provided'})

            # الآن يمكنك تمرير الاسم مباشرةً إلى دالة الحذف
            response = representative_manager.delete_record(representative_name)
            return jsonify(response)

        except Exception as e:
            print(f"Error in delete_representative route: {e}")
            return jsonify({'success': False, 'error': str(e)})
