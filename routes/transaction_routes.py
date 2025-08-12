# transaction_routes.py
from flask import render_template, request, send_file

from .auth_routes import login_required
from services.transaction_service import export_transactions_to_excel, fetch_transactions_from_db

def register_transaction_routes(app):
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