from flask import Blueprint, render_template, request, redirect, session, jsonify
from datetime import datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route('/')
def admin_dashboard():
    from db import phones_col, orders_col
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    phones = list(phones_col.find())
    orders = orders_col.sort('date', -1)
    
    return render_template('admin.html', phones=phones, orders=orders)

@admin_bp.route('/add_product', methods=['POST'])
def admin_add_product():
    from db import phones_col
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        phones_col.insert_one({
            "name": data['name'],
            "brand": data['brand'],
            "price": int(data['price']),
            "stock": int(data['stock']),
            "description": data['description'],
            "image": data.get('image', 'no-image.jpg'),
            "features": {},
            "specifications": {}
        })
        
        return jsonify({'success': True, 'message': 'Sản phẩm đã được thêm'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@admin_bp.route('/edit_product/<string:name>', methods=['POST'])
def admin_edit_product(name):
    from db import phones_col
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        phones_col.update_one(
            {'name': name},
            {'$set': {
                'name': data['name'],
                'brand': data['brand'],
                'price': int(data['price']),
                'stock': int(data['stock']),
                'description': data['description'],
                'image': data.get('image', 'no-image.jpg')
            }}
        )
        
        return jsonify({'success': True, 'message': 'Sản phẩm đã được cập nhật'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@admin_bp.route('/delete_product/<string:name>', methods=['POST'])
def admin_delete_product(name):
    from db import phones_col
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        phones_col.delete_one({'name': name})
        return jsonify({'success': True, 'message': 'Sản phẩm đã được xóa'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@admin_bp.route('/update_order_status/<string:order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    from db import orders_col
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        orders_col.update_one(
            {'_id': order_id},
            {'$set': {'status': data['status']}}
        )
        
        return jsonify({'success': True, 'message': 'Trạng thái đơn hàng đã được cập nhật'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400