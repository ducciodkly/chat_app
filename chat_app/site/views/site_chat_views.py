import functools
import datetime
from flask import Blueprint, render_template, request, jsonify,current_app
from flask_login import login_required, current_user
from flask_socketio import disconnect
from sqlalchemy import or_, desc
from chat_app import db, socketio   
from Helpers import row2dict
from chat_app.site.form import room_Form,add_user_to_room_Form,block_user_Form,send_message_Form,delete_room_Form
from Models.models import User, RoomParticipant, Room,Messenger,Receiver,UserBlocks
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from flask_socketio import join_room, leave_room, send, emit


site_chat_views_module = Blueprint('site_chat', __name__, template_folder='../templates')



@site_chat_views_module.route('/chat')
@login_required
def chat():
    return render_template('site/chat.html')

@site_chat_views_module.route('/chat/search_user',methods=['GET'])
@login_required
def search_auto():
    key_words = request.args.get('search',0,type=str)
    users = User.query.filter(User.username.like('%'+str(key_words)+'%')).all()
    users_list = []
    for x in users:
        d = row2dict(x)
        users_list.append(d)
    return jsonify(users=users_list)

 
 
@site_chat_views_module.route('/chat/get_user',methods=['GET'])
@login_required
def get_user():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    return jsonify(row2dict(user))

@site_chat_views_module.route('/create_room', methods=['POST'])
@jwt_required()
def create_room():
    try:
        current_user_id = get_jwt_identity()
        form = room_Form()

        
        new_room = Room(type=1, create_at=datetime.datetime.now(), status=1) 
        db.session.add(new_room)
        db.session.commit()

        user1_participant = RoomParticipant(room_id=new_room.id, user_id=current_user_id, status=1)
        user2_participant = RoomParticipant(room_id=new_room.id, user_id=form.user_id2.data, status=1)
        db.session.add_all([user1_participant, user2_participant])
        db.session.commit()
        
        current_app.logger.info('New chat room created with ID: %s', new_room.id)
        return jsonify({'message': 'New chat room created.', 'room_id': new_room.id}), 200
    except Exception as e:
        current_app.logger.error('Error creating new chat room: %s', e)
        return jsonify({'message': str(e)}), 500
    
    
@site_chat_views_module.route('/create_group_room', methods=['POST'])
@jwt_required()
def create_group_room():
    try:
        current_user_id = get_jwt_identity()
        form = room_Form()
        
        new_group_room = Room(type=2, create_at=datetime.datetime.now(), status=1) 
        db.session.add(new_group_room)
        db.session.commit()

        user1_participant = RoomParticipant(room_id=new_group_room.id, user_id=current_user_id, status=1)
        user2_participant = RoomParticipant(room_id=new_group_room.id, user_id=form.user_id2.data, status=1)
        db.session.add_all([user1_participant, user2_participant])
        db.session.commit()
        current_app.logger.info('New group chat room created with ID: %s', new_group_room.id)

        return jsonify({'message': 'New group chat room created.', 'room_id': new_group_room.id}), 200
    except Exception as e:
        current_app.logger.error('Error creating new group chat room: %s', e)

        return jsonify({'message': str(e)}), 500
    
@site_chat_views_module.route('/delete_room', methods=['DELETE'])
@jwt_required()
def delete_room():
    try:
        current_user_id = get_jwt_identity() 
        form = delete_room_Form()
        current_app.logger.debug(f'Attempting to find Room with ID: {form.room_id.data}.')
        room = Room.query.filter_by(id=form.room_id.data).first()
        
        if not room:
            current_app.logger.warning(f'Room with ID: {form.room_id.data} not found.')
            return jsonify({'message': 'Room not found.'}), 404
        current_app.logger.debug(f'Room found. Proceeding with deleting Room {form.room_id.data}.')
        RoomParticipant.query.filter_by(room_id=form.room_id.data).delete()
        Messenger.query.filter_by(room_id=form.room_id.data).delete()
        db.session.delete(room)
        db.session.commit()

        current_app.logger.info(f'Room {form.room_id.data} deleted successfully.')
        return jsonify({'message': f'Room {form.room_id.data} deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error occurred when deleting room: {e}')  
        return jsonify({'message': str(e)}), 500
    
    
@site_chat_views_module.route('/add_user_to_room', methods=['POST'])
@jwt_required()
def add_user_to_room():
    try:
        current_user_id = get_jwt_identity() 
        form = add_user_to_room_Form()
        room = Room.query.filter_by(id = form.room_id.data).first()
        
        if room.type != 2:
            current_app.logger.warning('Attempted to add user to non-group room.')
            return jsonify({'message': 'Only group chat rooms can add new users.'}), 400

        existing_participant = RoomParticipant.query.filter_by(room_id=form.room_id.data, user_id=form.user_id.data).first()
        if existing_participant :
            current_app.logger.warning('User already a participant in the room.')
            return jsonify({'message': 'User already in the room.'}), 400
     
        new_participant = RoomParticipant(room_id=form.room_id.data, user_id=form.user_id.data, status=1)
        db.session.add(new_participant)
        db.session.commit()

        current_app.logger.info(f'User {form.user_id.data} added successfully to room {form.room_id.data}.')
        return jsonify({'message': f'User {form.user_id.data} added to room {form.room_id.data}.'}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error adding user to room: {e}')
        return jsonify({'message': str(e)}), 500

@site_chat_views_module.route('/block_user_from_room', methods=['POST'])
@jwt_required()
def block_user_from_room():
    try:
        current_user_id = get_jwt_identity() 
        form = add_user_to_room_Form()
        participant = RoomParticipant.query.filter_by(room_id=form.room_id.data, user_id=form.user_id.data).first()
        if participant:
            participant.status = 0
            db.session.commit()
            current_app.logger.info(f'User {form.user_id.data} blocked successfully from room {form.room_id.data}.')
            return jsonify({'message': f'User {form.user_id.data} blocked from room {form.room_id.data}.'}), 200
        else:
            current_app.logger.warning('User or room not found for blocking.')
            return jsonify({'message': 'User or room not found.'}), 404
    except Exception as e:
        current_app.logger.error(f'Unexpected error blocking user from room: {e}')
        return jsonify({'message': str(e)}), 500

@site_chat_views_module.route('/block_user', methods=['POST'])
@jwt_required()
def block_user():
    try:
        current_user_id = get_jwt_identity() 
        form = block_user_Form()

        if not User.query.get(form.blocked_id.data):
            current_app.logger.warning('Attempted to block a non-existent user')
            return jsonify({'message': 'User not found'}), 404

        if UserBlocks.query.filter_by(blocker_id=current_user_id, blocked_id=form.blocked_id.data).first():
            current_app.logger.warning('Attempted to block an already blocked user')
            return jsonify({'message': 'User already blocked'}), 409
        current_app.logger.info(f'User {form.blocked_id.data} successfully blocked by user {current_user_id}')
        new_block = UserBlocks(blocker_id=current_user_id, blocked_id=form.blocked_id.data)
        db.session.add(new_block)
        db.session.commit()

        return jsonify({'message': 'User blocked'}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error when trying to block user: {e}')
        return jsonify({'message': str(e)}), 500

@site_chat_views_module.route('/unblock_user', methods=['POST'])
@jwt_required()
def unblock_user():
    try:
        current_user_id = get_jwt_identity() 
        form = block_user_Form()

        user_block = UserBlocks.query.filter_by(
            blocker_id=current_user_id,
            blocked_id=form.blocked_id.data
        ).first()

        if not user_block:
            current_app.logger.warning('Attempted to unblock user who is not blocked')
            return jsonify({'error': "User not blocked."}), 400
        db.session.delete(user_block)
        db.session.commit()
        current_app.logger.info(f'User {form.blocked_id.data} successfully unblocked by user {current_user_id}')
        return jsonify({'message': 'User unblocked'}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error when trying to unblock user: {e}')
        return jsonify({'message': str(e)}), 500

@site_chat_views_module.route('/send_message', methods=['POST'])
@jwt_required()
def send_message():
    try:
        current_user_id = get_jwt_identity()
        form = send_message_Form()
        
        new_message = Messenger(sender_id=current_user_id, room_id=form.room_id.data, content=form.content.data, status=1)
        db.session.add(new_message)
        db.session.flush()
        current_app.logger.debug(f'New message by {current_user_id} staged for room {form.room_id.data}.')
    

        participants = db.session.query(RoomParticipant.user_id).outerjoin(UserBlocks, 
                (UserBlocks.blocked_id == RoomParticipant.user_id) & (UserBlocks.blocker_id == current_user_id) | 
                (UserBlocks.blocker_id == RoomParticipant.user_id) & (UserBlocks.blocked_id == current_user_id)
                ).filter(RoomParticipant.room_id == form.room_id.data, UserBlocks.id == None).all()
        for participant in participants:
            if participant.user_id != current_user_id:
                receiver = Receiver(message_id=new_message.id, receiver_id=participant.user_id)
                db.session.add(receiver)
            current_app.logger.debug(f'Message receiver added: {participant.user_id}.')
        
        db.session.commit()
        current_app.logger.info(f'Message sent successfully to room {form.room_id.data}.')
        return jsonify({'message': 'Message sent.'}), 200
    except Exception as e:
        current_app.logger.error(f'Failed to send message: {e}')
        return jsonify({'message': str(e)}), 500


@site_chat_views_module.route('/get_messages/<int:room_id>', methods=['GET'])
@jwt_required()
def get_messages(room_id):
    current_user_id = get_jwt_identity()
    current_app.logger.info(f'Fetching messages for room {room_id}')
    try:
        messages = Messenger.query.filter_by(room_id=room_id, status=1).all()  
        messages_data = [{'id': message.id, 'sender_id': message.sender_id, 'content': message.content, 'create_at': message.create_at} for message in messages]
        current_app.logger.debug(f'Total messages fetched: {len(messages_data)} for room {room_id}')
        return jsonify(messages_data), 200
    except Exception as e:
        current_app.logger.error(f'Failed to fetch messages for room {room_id}: {e}')
        return jsonify({'message': str(e)}), 500

@site_chat_views_module.route('/get_messages_users/<int:sender_id>', methods=['GET'])
def get_messages_by_user_id(sender_id):
    try:
        messages = Messenger.query.filter_by(sender_id=sender_id, status=1).all()  
        messages_data = [{'id': message.id, 'room_id': message.room_id, 'content': message.content, 'create_at': message.create_at} for message in messages]
        return jsonify(messages_data), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(f"{username} has entered the room.", to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f"{username} has left the room.", to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    user_id = data['user_id']
    message_content = data['message']
    
    message = Messenger(sender_id=user_id, room_id=room, content=message_content)
    db.session.add(message)
    db.session.commit()

    emit('new_message', {'user_id': user_id, 'message': message_content}, to=room)


#validate 
#đặt log
#middle ware lấy current user từ token







