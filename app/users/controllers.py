from flask import request, make_response, json, send_file, session
from flask_login import login_required, current_user
import app.users.models as model


@login_required
def get_profile():
    return make_response(json.jsonify(current_user.profile), 200)


@login_required
def get_thumbnail(picture_name):
    picture = model.select_user_thumbnail(current_user.idx)
    return send_file(picture, mimetype='image/jpeg')


@login_required
def get_thumbnail_original(picture_name):
    picture = model.select_user_thumbnail_original(current_user.idx)
    return send_file(picture, mimetype='image/jpeg')


@login_required
def change_password():
    new_pwd = request.form.get('new_pwd', None)

    if None in [new_pwd]:
        return make_response(json.jsonify(result='Something Not Entered'), 460)
    #: 비밀번호 검사
    elif len(new_pwd) < 4:
        return make_response(json.jsonify(result='Password must be at least 4 digits'), 467)

    is_done = model.update_password(current_user.id, new_pwd)

    if is_done == 1:
        return make_response(json.jsonify(result='Password changed successfully!'), 200)
    elif is_done == 2:
        return make_response(json.jsonify(result='Password is wrong'), 465)
    elif is_done == 0:
        return make_response(json.jsonify(result='Something Wrong'), 461)


@login_required
def change_nickname():
    nickname = request.form.get('nickname', None)
    if nickname is None:
        return make_response(json.jsonify(result='Something Not Entered'), 460)

    is_done = model.update_nickname(current_user.id, nickname)

    if is_done is True:
        session['user_nickname'] = nickname
        return make_response(json.jsonify(result='Nickname changed successfully!'), 200)
    else:
        return make_response(json.jsonify(result='Something Wrong'), 461)


@login_required
def change_picture():
    picture = request.files.get('picture', None)
    if picture is None:
        return make_response(json.jsonify(result='Something Not Entered'), 460)

    is_done, user_picture = model.update_picture(current_user.id, picture)

    if is_done is 1:
        session['user_picture'] = user_picture
        return make_response(json.jsonify(result='Picture changed successfully!'), 200)
    elif is_done is 2:
        return make_response(json.jsonify(result='Picture upload failed'), 468)
    else:
        return make_response(json.jsonify(result='Something Wrong'), 461)


@login_required
def user_withdraw():
    is_done = model.delete_user(current_user.idx)

    if is_done is True:
        return make_response(json.jsonify(result='You successfully left Mycattool'), 200)
    else:
        return make_response(json.jsonify(result='Something Wrong'), 461)
