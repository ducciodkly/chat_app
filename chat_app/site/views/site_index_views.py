import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, request
from flask_login import login_required, current_user
from chat_app import db, AVATAR_UPOLAD_DIRECTORY

site_index_views_module = Blueprint('site_index', __name__, template_folder='../templates')


@site_index_views_module.route('/')
@login_required
def index():
    return render_template('site/index.html')


@site_index_views_module.route('/update-profile', methods=['POST'])
@login_required
def profile_update():
    current_user.username = request.form['username']
    current_user.phone = request.form['phone']

    for file in request.files.getlist("avatar"):
        if current_user.avatar:
            old_file_name = current_user.avatar
            old_file_path = "/".join([AVATAR_UPOLAD_DIRECTORY, old_file_name])
            os.remove(old_file_path)
        now = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        new_file_name = now + '_' + current_user.username + '_' + file.filename
        new_file_path = "/".join([AVATAR_UPOLAD_DIRECTORY, new_file_name])
        file.save(new_file_path)
        current_user.avatar = new_file_name

    db.session.commit()
    return redirect('/')


