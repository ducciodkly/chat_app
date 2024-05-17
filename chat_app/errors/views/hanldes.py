from flask import Blueprint, jsonify,render_template

errors_handle_module = Blueprint('errors', __name__,template_folder='../templates')


@errors_handle_module.app_errorhandler(404)
def error_404(error):
    # return jsonify({'message': '404 Not Found'}), 404
    return render_template('errors/404.html'), 404
 

@errors_handle_module.app_errorhandler(403)
def error_403(error):
    # return jsonify({'message':"403 Not permiss to do that"}), 403
    return render_template('errors/403.html'), 403


@errors_handle_module.app_errorhandler(500)
def error_500(error):
    return jsonify({'message':"500 Something went wrong"}), 500
    # return render_template('errors/500.html'), 500
