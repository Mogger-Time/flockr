import auth
import other
import message
import channel
import channels
import data
import pytest
from error import InputError
from error import AccessError

# test functions for users_all
def test_users_all_invalid_token():
    other.clear()
    with pytest.raises(AccessError):
        other.users_all("invalid_token")
        other.users_all("")

def test_users_all_successful():
    other.clear()
    first_user = auth.auth_register("user1@email.com", "password123", "First", "User")
    assert other.users_all(first_user['token']) == [{'u_id' : first_user['u_id'], 'email' : "user1@email.com", 'name_first' : "First", 'name_last' : "User", 'handle_str' : "firstuser"}]

    second_user = auth.auth_register("user2@email.com", "password321", "Second", "User")
    assert other.users_all(second_user['token']) == [{'u_id' : first_user['u_id'], 'email' : "user1@email.com", 'name_first' : "First", 'name_last' : "User", 'handle_str' : "firstuser"},
                                                    {'u_id' : second_user['u_id'], 'email' : "user2@email.com", 'name_first' : "Second", 'name_last' : "User", 'handle_str' : "seconduser"}]

# test functions for admin_userpermission_change
def test_admin_userpermission_change_invalid_id():
    other.clear()
    login_owner = auth.auth_register("owner@email.com", "password123", "Owner", "Test")
    login_user = auth.auth_register("user@email.com", "password321", "User", "Test")
    invalid_u_id = -1
    invalid_permission_id = -1

    with pytest.raises(InputError):
        other.admin_userpermission_change(login_owner['token'], invalid_u_id, 1)
        other.admin_userpermission_change(login_owner['token'], login_user['u_id'], invalid_permission_id)
        other.admin_userpermission_change(login_owner['token'], invalid_u_id, invalid_permission_id)

def test_admin_userpermission_change_invalid_token():
    other.clear()
    login_owner = auth.auth_register("owner@email.com", "password123", "Owner", "Test")
    login_user = auth.auth_register("user@email.com", "password321", "User", "Test")

    with pytest.raises(AccessError):
        other.admin_userpermission_change("", login_user['u_id'], 1)
        other.admin_userpermission_change(login_user['token'], login_owner['u_id'], 2)

def test_admin_userpermission_change_success():
    other.clear()
    login_owner = auth.auth_register("owner@email.com", "password123", "Owner", "Test")
    login_user = auth.auth_register("user@email.com", "password321", "User", "Test")

    other.admin_userpermission_change(login_owner['token'], login_user['u_id'], 1)
    other.admin_userpermission_change(login_user['token'], login_owner['u_id'], 2)

    with pytest.raises(AccessError):
        other.admin_userpermission_change(login_owner['token'], login_user['u_id'], 2)

# test functions for search
def test_search_empty():
    other.clear()
    login = auth.auth_register("user@email.com", "password123", "User", "Test")

    channel_id = channels.channels_create(login['token'], "channel", True)
    message.message_send(login['token'], channel_id, "message")

    assert other.search(login['token'], "") == {[]}

def test_search_own_channel_single_message_complete():
    other.clear()
    login = auth.auth_register("user@email.com", "password123", "User", "Test")

    channel_id = channels.channels_create(login['token'], "channel", True)
    message_id = message.message_send(login['token'], channel_id, "message")

    assert other.search(login['token'], "message") == {[{'message_id' : message_id, 'u_id' : login['u_id'], 'message' : "message", 'time_created' : data.data['messages'][0]['time_created']}]}

def test_search_own_channel_single_message_incomplete():
    other.clear()
    login = auth.auth_register("user@email.com", "password123", "User", "Test")

    channel_id = channels.channels_create(login['token'], "channel", True)
    message_id = message.message_send(login['token'], channel_id, "message")

    assert other.search(login['token'], "ess") == {[{'message_id' : message_id, 'u_id' : login['u_id'], 'message' : "message", 'time_created' : data.data['messages'][0]['time_created']}]}

def test_search_other_channel_single_message_complete():
    other.clear()
    login_owner = auth.auth_register("owner@email.com", "password123", "Owner", "Test")
    login_user = auth.auth_register("user@email.com", "password321", "User", "Test")

    channel_id = channels.channels_create(login_owner['token'], "channel", True)
    channel.channel_join(login_user['token'], channel_id['channel_id'])

    message_id = message.message_send(login_owner['token'], channel_id, "message")

    assert other.search(login_user['token'], "message") == {[{'message_id' : message_id, 'u_id' : login_owner['u_id'], 'message' : "message", 'time_created' : data.data['messages'][0]['time_created']}]}

def test_search_other_channel_single_message_incomplete():
    other.clear()
    login_owner = auth.auth_register("owner@email.com", "password123", "Owner", "Test")
    login_user = auth.auth_register("user@email.com", "password321", "User", "Test")

    channel_id = channels.channels_create(login_owner['token'], "channel", True)
    channel.channel_join(login_user['token'], channel_id['channel_id'])

    message_id = message.message_send(login_owner['token'], channel_id, "message")

    assert other.search(login_user['token'], "ess") == {[{'message_id' : message_id, 'u_id' : login_owner['u_id'], 'message' : "message", 'time_created' : data.data['messages'][0]['time_created']}]}

def test_search_both_channels_two_messages_complete():
    other.clear()
    login_owner = auth.auth_register("owner@email.com", "password123", "Owner", "Test")
    login_user = auth.auth_register("user@email.com", "password321", "User", "Test")

    channel_id1 = channels.channels_create(login_owner['token'], "channel1", True)
    channel.channel_join(login_user['token'], channel_id1['channel_id'])

    channel_id2 = channels.channels_create(login_user['token'], "channel2", True)

    message_id1 = message.message_send(login_owner['token'], channel_id1, "message")
    message_id2 = message.message_send(login_user['token'], channel_id2, "message")

    assert other.search(login_user['token'], "message") == {[{'message_id' : message_id1, 'u_id' : login_owner['u_id'], 'message' : "message", 'time_created' : data.data['messages'][0]['time_created']},
                                                            {'message_id' : message_id2, 'u_id' : login_user['u_id'], 'message' : "message", 'time_created' : data.data['messages'][1]['time_created']}]}

def test_search_both_channels_two_messages_incomplete():
    other.clear()
    login_owner = auth.auth_register("owner@email.com", "password123", "Owner", "Test")
    login_user = auth.auth_register("user@email.com", "password321", "User", "Test")

    channel_id1 = channels.channels_create(login_owner['token'], "channel1", True)
    channel.channel_join(login_user['token'], channel_id1['channel_id'])

    channel_id2 = channels.channels_create(login_user['token'], "channel2", True)

    message_id1 = message.message_send(login_owner['token'], channel_id1, "message")
    message_id2 = message.message_send(login_user['token'], channel_id2, "messages")

    assert other.search(login_user['token'], "ess") == {[{'message_id' : message_id1, 'u_id' : login_owner['u_id'], 'message' : "message", 'time_created' : data.data['messages'][0]['time_created']},
                                                        {'message_id' : message_id2, 'u_id' : login_user['u_id'], 'message' : "messages", 'time_created' : data.data['messages'][1]['time_created']}]}

def test_search_own_channel_single_message_excluding_other_channel():
    other.clear()
    login_owner = auth.auth_register("owner@email.com", "password123", "Owner", "Test")
    login_user = auth.auth_register("user@email.com", "password321", "User", "Test")

    channel_id1 = channels.channels_create(login_owner['token'], "channel1", True)
    channel_id2 = channels.channels_create(login_user['token'], "channel2", True)

    message.message_send(login_owner['token'], channel_id1, "message")
    message_id2 = message.message_send(login_user['token'], channel_id2, "message")

    assert other.search(login_user['token'], "message") == {[{'message_id' : message_id2, 'u_id' : login_user['u_id'], 'message' : "message", 'time_created' : data.data['messages'][1]['time_created']}]}