from flask import render_template, request, jsonify

def is_api_request():
    return request.path.startswith('/api/')

def page_not_found(e):
    if is_api_request():
        return jsonify({'error': 'Not found', 'message': 'Requested resource not found'}), 404
    return render_template('errors/404.html'), 404

def internal_server_error(e):
    if is_api_request():
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
    return render_template('errors/500.html'), 500 