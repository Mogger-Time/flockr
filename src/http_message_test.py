from time import sleep
from subprocess import Popen, PIPE
import json
import re
import signal
import pytest
import requests
from error import InputError
from error import AccessError
from other import clear

# Use this fixture to get the URL of the server.
@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

def test_url(url):
    """Tests that the server has been set up properly."""
    assert url.startswith("http")

# Register owner function
def reg_owner(url):
    """Registers an owner, the original owner of the Flock."""
    register_owner = {
        'email': "owner@email.com",
        'password': "password123",
        'name_first': "Owner",
        'name_last': "Test"
    }
    r = requests.post(url + "auth/register", json=register_owner)
    return r.json()

# Register user function
def reg_user(url):
    """Registers a user."""
    register_user = {
        'email': "user@email.com",
        'password': "password321",
        'name_first': "User",
        'name_last': "Test"
    }
    r = requests.post(url + "auth/register", json=register_user)
    return r.json()

#create channel function
def create_channel(url, login_owner):
    channels_create = {
        'token': login_owner['token'],
        'name': "channel",
        'is_public': True
    }
    r = requests.post(url + "channels/create", json=channels_create)
    return r.json()

#invite user function
def inv_user(url, login_owner, login_user, channel_id):
    invite_user = {
        'token': login_owner['token'],
        'channel_id': channel_id['channel_id'],
        'u_id': login_user['u_id']
    }
    requests.post(url + "channel/invite", json=invite_user)

#message send function
def msg_send(url, user, channel, message):
    message_send = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': message
    }
    r = requests.post(url + "message/send", json=message_send)
    return r.json()

#create unique channel function
def create_unique_channel(url, user, name, is_public):
    channel = {
        'token': user['token'],
        'name': name,
        'is_public': is_public
    }
    r = requests.post(url + "channels/create", json=channel)
    return r.json()

#pin message function
def pin(url, user, message):
    pin_message = {
        'token': user['token'],
        'message_id': message['message_id']
    }
    r = requests.post(url + "message/pin", json=pin_message)
    return r.json()

#unpin message function
def unpin(url, user, message):
    unpin_message = {
        'token': user['token'],
        'message_id': message['message_id']
    }
    r = requests.post(url + "message/unpin", json=unpin_message)
    return r.json()

#join channel function
def join_channel(url, user, channel):
    join = {
        'token': user['token'],
        'channel_id': channel['channel_id']
    }
    r = requests.post(url + "channel/join", json=join)
    return r.json()

#leave channel function
def leave_channel(url, user, channel):
    leave = {
        'token': user['token'],
        'channel_id': channel['channel_id']
    }
    r = requests.post(url + "channel/leave", json=leave)
    return r.json()

# Tests for message_send
def test_http_message_send_input_error(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)
    
    large_string_1 = {
        "token": login_owner["token"],
        "channel_id": channel_id["channel_id"],
        "message": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure? On the other hand, we denounce"
    }

    r = requests.post(url + "message/send", json=large_string_1)
    payload = r.json()
    assert payload["message"] == "<p>Message is larger than 1000 characters</p>"
    assert payload["code"] == 400

    large_string_2 = {
        "token": login_owner["token"],
        "channel_id": channel_id["channel_id"],
        "message": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores e"
    }

    r = requests.post(url + "message/send", json=large_string_2)
    payload = r.json()
    assert payload["message"] == "<p>Message is larger than 1000 characters</p>"
    assert payload["code"] == 400

    large_string_3 = {
        "token": login_owner["token"],
        "channel_id": channel_id["channel_id"],
        "message": "Li Europan lingues es membres del sam familie. Lor separat existentie es un myth. Por scientie, musica, sport etc, litot Europa usa li sam vocabular. Li lingues differe solmen in li grammatica, li pronunciation e li plu commun vocabules. Omnicos directe al desirabilite de un nov lingua franca: On refusa continuar payar custosi traductores. At solmen va esser necessi far uniform grammatica, pronunciation e plu sommun paroles. Ma quande lingues coalesce, li grammatica del resultant lingue es plu simplic e regulari quam ti del coalescent lingues. Li nov lingua franca va esser plu simplic e regulari quam li existent Europan lingues. It va esser tam simplic quam Occidental in fact, it va esser Occidental. A un Angleso it va semblar un simplificat Angles, quam un skeptic Cambridge amico dit me que Occidental es. Li Europan lingues es membres del sam familie. Lor separat existentie es un myth. Por scientie, musica, sport etc, litot Europa usa li sam vocabular. Li lingues differe solmen in li g"
    }

    r = requests.post(url + "message/send", json=large_string_3)
    payload = r.json()
    assert payload["message"] == "<p>Message is larger than 1000 characters</p>"
    assert payload["code"] == 400

    non_existent_channel_id = {
        "token": login_owner["token"],
        "channel_id": -1,
        "message": "sample message"
    }

    r = requests.post(url + "message/send", json=non_existent_channel_id)
    payload = r.json()
    assert payload["message"] == "<p>Invalid channel</p>"
    assert payload["code"] == 400

def test_http_message_send_access_error(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)
    login_user = reg_user(url)

    invalid_user = {
        "token": login_user["token"],
        "channel_id": channel_id["channel_id"],
        "message": "sample message"
    }

    r = requests.post(url + "message/send", json=invalid_user)
    payload = r.json()
    assert payload["message"] == "<p>The user has not joined the channel they are trying to post to</p>"
    assert payload["code"] == 400

def test_http_message_send_success(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)
    login_user = reg_user(url)
    inv_user(url, login_owner, login_user, channel_id)

    message_1 = {
        "token": login_owner["token"],
        "channel_id": channel_id["channel_id"],
        "message": "sample message"
    }

    r = requests.post(url + "message/send", json=message_1)
    payload = r.json()
    assert payload["message_id"] == 0

    message_2 = {
        "token": login_user["token"],
        "channel_id": channel_id["channel_id"],
        "message": "sample message"
    }

    r = requests.post(url + "message/send", json=message_2)
    payload = r.json()
    assert payload["message_id"] == 1

    message_3 = {
        "token": login_owner["token"],
        "channel_id": channel_id["channel_id"],
        "message": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores."
    }

    r = requests.post(url + "message/send", json=message_3)
    payload = r.json()
    assert payload["message_id"] == 2

    message_4 = {
        "token": login_user["token"],
        "channel_id": channel_id["channel_id"],
        "message": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores."
    }

    r = requests.post(url + "message/send", json=message_4)
    payload = r.json()
    assert payload["message_id"] == 3

# Tests for message_remove
def test_http_message_remove_no_messages(url):
    clear()
    login_owner = reg_owner(url)
    create_unique_channel(url, login_owner, "channel", True)

    no_messages = {
        "token": login_owner["token"],
        "message_id": 1
    }

    r = requests.delete(url + 'message/remove', json=no_messages)
    payload = r.json()

    assert payload["message"] == "<p>Message has already been deleted</p>"
    assert payload["code"] == 400

def test_http_message_remove_removed_message(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example message")
    message_to_remove = {
        "token": login_owner["token"],
        "message_id": 0
    }
    requests.delete(url + 'message/remove', json=message_to_remove)

    removed_message = {
        "token": login_owner["token"],
        "message_id": 0
    }

    r = requests.delete(url + 'message/remove', json=removed_message)
    payload = r.json()
    assert payload["message"] == "<p>Message has already been deleted</p>"
    assert payload["code"] == 400

def test_http_message_remove_not_message_sender(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)
    login_user = reg_user(url)
    msg_send(url, login_owner, channel_id, "example message")

    message_to_remove = {
        "token": login_user["token"],
        "message_id": 0
    }

    r = requests.delete(url + 'message/remove', json=message_to_remove)
    payload = r.json()
    assert payload["message"] == "<p>User is not a flock owner or the original user who sent the message</p>"
    assert payload["code"] == 400 

def test_http_message_remove_admin_remove_success(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)
    login_user = reg_user(url)
    inv_user(url, login_owner, login_user, channel_id)
    
    msg_send(url, login_user, channel_id, "example_message")

    message_to_remove = {
        "token": login_owner["token"],
        "message_id": 0
    }

    requests.delete(url + 'message/remove', json=message_to_remove)

    r = requests.get(url + 'channel/messages', params={"token": login_owner["token"], "channel_id": channel_id["channel_id"], "start": 0})
    payload = r.json()
    assert payload["start"] == 0
    assert payload["end"] == -1

# Tests for message_edit
def test_http_edit_1000_characters(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    thousand_character = {
        "token": login_owner["token"],
        "message_id": 0,
        "message": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure? On the other hand, we denounce"
    }

    r = requests.put(url + 'message/edit', json=thousand_character)
    payload = r.json()
    assert payload["message"] == "<p>Message is larger than 1000 characters</p>"
    assert payload["code"] == 400

def test_http_message_edit_not_message_sender(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)
    login_user = reg_user(url)
    inv_user(url, login_owner, login_user, channel_id)

    msg_send(url, login_owner, channel_id, "example_message")

    edit = {
        "token": login_user["token"],
        "message_id": 0,
        "message": "edited message"
    }

    r = requests.put(url + 'message/edit', json=edit)
    payload = r.json()
    assert payload["message"] == "<p>User is not a flock owner or the original user who sent the message</p>"
    assert payload["code"] == 400

def test_http_message_edit_owner_success(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)
    login_user = reg_user(url)
    inv_user(url, login_owner, login_user, channel_id)

    msg_send(url, login_user, channel_id, "example_message")

    edit = {
        "token": login_owner["token"],
        "message_id": 0,
        "message": "edited message"
    }
    requests.put(url + 'message/edit', json=edit)

    r = requests.get(url + 'channel/messages', params={"token": login_owner["token"], "channel_id": channel_id["channel_id"], "start": 0})
    payload = r.json()
    assert payload["messages"][0]["message"] == "edited message"
    
# Tests for message_pin

def http_test_message_pin_success():
    '''test for successful pin'''
    clear()
    login_owner = reg_owner(url)
    channel_id = create_channel(url, login_owner)
    message_id = msg_send(url, login_owner, channel_id, "sample message")

    empty = pin(url, login_owner, message_id)

    assert empty == {}

def http_test_message_pin_invalid_message_id():
    '''test for input error due to invalid message id'''
    clear()
    login_owner = reg_owner(url)
    create_channel(url, login_owner)
    invalid_message_id = -1

    payload = pin(url, login_owner, invalid_message_id)

    assert payload['message'] == "<p>Message is not a valid message</p>"
    assert payload['code'] == 400

def http_test_message_pin_already_pinned():
    '''test for input error due to message already being pinned'''
    clear()
    login_owner = reg_owner(url)
    channel_id = create_channel(url, login_owner)
    message_id = msg_send(url, login_owner, channel_id, "sample message")

    pin(url, login_owner, message_id)

    payload = pin(url, login_owner, message_id)

    assert payload['message'] == "<p>Message is already pinned</p>"
    assert payload['code'] == 400

def http_test_message_pin_invalid_channel():
    '''test for access error due to user not being in the channel the message is in'''
    clear()
    login_owner = reg_owner(url)
    channel_id = create_channel(url, login_owner)
    message_id = msg_send(url, login_owner, channel_id, "sample message")

    leave_channel(url, login_owner, channel_id)

    payload = pin(url, login_owner, message_id)

    assert payload['message'] == "<p>User is not a member of the channel or an owner in the channel</p>"
    assert payload['code'] == 400

def http_test_message_pin_not_owner():
    '''test for access error due to user not being an owner in the channel'''
    clear()
    login_owner = reg_owner(url)
    channel_id = create_channel(url, login_owner)
    message_id = msg_send(url, login_owner, channel_id, "sample message")

    login_user = reg_user(url)
    join_channel(url, login_user, channel_id)

    payload = pin(url, login_user, message_id)

    assert payload['message'] == "<p>User is not a member of the channel or an owner in the channel</p>"
    assert payload['code'] == 400

# Tests for message_unpin

def http_test_message_unpin_success():
    '''test for successful unpin'''
    clear()
    login_owner = reg_owner(url)
    channel_id = create_channel(url, login_owner)
    message_id = msg_send(url, login_owner, channel_id, "sample message")

    pin(url, login_owner, message_id)

    empty = unpin(url, login_owner, message_id)

    assert empty == {}

def http_test_message_unpin_invalid_message_id():
    '''test for input error due to invalid message id'''
    clear()
    login_owner = reg_owner(url)
    create_channel(url, login_owner)
    invalid_message_id = -1

    payload = unpin(url, login_owner, invalid_message_id)

    assert payload['message'] == "<p>Message is not a valid message</p>"
    assert payload['code'] == 400

def http_test_message_unpin_already_unpinned():
    '''test for input error due to message already being unpinned'''
    clear()
    login_owner = reg_owner(url)
    channel_id = create_channel(url, login_owner)
    message_id = msg_send(url, login_owner, channel_id, "sample message")

    pin(url, login_owner, message_id)

    unpin(url, login_owner, message_id)

    payload = unpin(url, login_owner, message_id)

    assert payload['message'] == "<p>Message is already unpinned</p>"
    assert payload['code'] == 400

def http_test_message_unpin_invalid_channel():
    '''test for access error due to user not being in the channel the message is in'''
    clear()
    login_owner = reg_owner(url)
    channel_id = create_channel(url, login_owner)
    message_id = msg_send(url, login_owner, channel_id, "sample message")

    pin(url, login_owner, message_id)

    leave_channel(url, login_owner, channel_id)

    payload = unpin(url, login_owner, message_id)

    assert payload['message'] == "<p>User is not a member of the channel or an owner in the channel</p>"
    assert payload['code'] == 400

def http_test_message_unpin_not_owner():
    '''test for access error due to user not being an owner in the channel'''
    clear()
    login_owner = reg_owner(url)
    channel_id = create_channel(url, login_owner)
    message_id = msg_send(url, login_owner, channel_id, "sample message")

    login_user = reg_user(url)
    join_channel(url, login_user, channel_id)

    pin(url, login_owner, message_id)

    payload = unpin(url, login_user, message_id)

    assert payload['message'] == "<p>User is not a member of the channel or an owner in the channel</p>"
    assert payload['code'] == 400

# TEST FUNCTIONS FOR HTTP_MESSAGE_SENDLATER
# Failure for send later
def test_http_message_sendlater_invalid_token(url):
    "Tests for failure when the token is invalid"
    clear()
    login_owner = reg_owner(url)
    channel_info = create_channel(url, login_owner)

    invalid_token = {
        "token": "invalid_token",
        "channel_id": channel_info["channel_id"],
        "message": "Hello World",
        "time_sent": 1609459200
    }
    r = requests.post(url + 'message/sendlater', json=invalid_token)
    payload = r.json()
    assert payload["message"] == "<p>Invalid permissions</p>"
    assert payload["code"] == 400

def test_http_message_sendlater_invalid_channel(url):
    "Tests for failure when the user inputs an invalid channel_id"
    clear()
    login_owner = reg_owner(url)

    invalid_channel_id1 = {
        "token": login_owner["token"],
        "channel_id": -1,
        "message": "Hello World",
        "time_sent": 1609459200
    }
    r = requests.post(url + 'message/sendlater', json=invalid_channel_id1)
    payload = r.json()
    assert payload["message"] == "<p>Invalid channel</p>"
    assert payload["code"] == 400

    invalid_channel_id2 = {
        "token": login_owner["token"],
        "channel_id": 100,
        "message": "Python is cool Python is cool Python is cool Python is cool Python is cool Python is cool Python is cool Python is cool",
        "time_sent": 1609459200
    }
    r = requests.post(url + 'message/sendlater', json=invalid_channel_id2)
    payload = r.json()
    assert payload["message"] == "<p>Invalid channel</p>"
    assert payload["code"] == 400

def test_http_message_sendlater_over_1000_chars(url):
    "Tests for failure when the user inputs a message over 1000 characters in length"
    clear()
    login_owner = reg_owner(url)
    channel_info = create_channel(url, login_owner)

    msg_over_1000 = {
        "token": login_owner["token"],
        "channel_id": channel_info["channel_id"],
        "message": "Li Europan lingues es membres del sam familie. Lor separat existentie es un myth. Por scientie, musica, sport etc, litot Europa usa li sam vocabular. Li lingues differe solmen in li grammatica, li pronunciation e li plu commun vocabules. Omnicos directe al desirabilite de un nov lingua franca: On refusa continuar payar custosi traductores. At solmen va esser necessi far uniform grammatica, pronunciation e plu sommun paroles. Ma quande lingues coalesce, li grammatica del resultant lingue es plu simplic e regulari quam ti del coalescent lingues. Li nov lingua franca va esser plu simplic e regulari quam li existent Europan lingues. It va esser tam simplic quam Occidental in fact, it va esser Occidental. A un Angleso it va semblar un simplificat Angles, quam un skeptic Cambridge amico dit me que Occidental es. Li Europan lingues es membres del sam familie. Lor separat existentie es un myth. Por scientie, musica, sport etc, litot Europa usa li sam vocabular. Li lingues differe solmen in li g",
        "time_sent": 1609459200
    }
    r = requests.post(url + 'message/sendlater', json=msg_over_1000)
    payload = r.json()
    assert payload["message"] == "<p>Message is larger than 1000 characters</p>"
    assert payload["code"] == 400

def test_http_message_sendlater_time_in_past(url):
    "Tests for failure when the user inputs a time that has already passed"
    clear()
    login_owner = reg_owner(url)
    channel_info = create_channel(url, login_owner)

    invalid_time = {
        "token": login_owner["token"],
        "channel_id": channel_info["channel_id"],
        "message": "Hello World",
        "time_sent": 1577836800
    }
    r = requests.post(url + 'message/sendlater', json=invalid_time)
    payload = r.json()
    assert payload["message"] == "<p>Time has already passed</p>"
    assert payload["code"] == 400
    
def test_http_message_sendlater_access_error(url):
    "Tests for failure when a user tries to send a message later in a channel they are not in"
    clear()
    login_owner = reg_owner(url)
    channel_info = create_channel(url, login_owner)
    login_user = reg_user(url)

    invalid_access = {
        "token": login_user["token"],
        "channel_id": channel_info["channel_id"],
        "message": "Hello World",
        "time_sent": 1609459200
    }
    r = requests.post(url + 'message/sendlater', json=invalid_access)
    payload = r.json()
    assert payload["message"] == "<p>The user has not joined the channel they are trying to post to</p>"
    assert payload["code"] == 400

    # Tests for message_react
def test_http_message_react_message_does_not_exist(url):
    clear()
    login_owner = reg_owner(url)
    create_unique_channel(url, login_owner, "channel", True)

    react = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 1
    }

    r = requests.post(url + "message/react", json=react)
    payload = r.json()
    assert payload["message"] == "<p>Specified message does not exist</p>"
    assert payload["code"] == 400

def test_http_message_react_removed_message(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")
    
    remove = {
        "token": login_owner["token"],
        "message_id": 0
    }

    requests.delete(url + "message/remove", json=remove)

    react = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 1
    }

    r = requests.post(url + "message/react", json=react)
    payload = r.json()
    assert payload["message"] == "<p>Specified message does not exist</p>"
    assert payload["code"] == 400

def test_http_message_react_message_in_private_channel(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", False)
    login_user = reg_user(url)

    msg_send(url, login_owner, channel_id, "example_message")

    react = {
        "token": login_user["token"],
        "message_id": 0,
        "react_id": 1
    }

    r = requests.post(url + "message/react", json=react)
    payload = r.json()
    assert payload["message"] == "<p>User is not currently in the channel of the message they are trying to react to</p>"
    assert payload["code"] == 400

def test_http_message_react_react_id_0(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    react = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 0
    }

    r = requests.post(url + "message/react", json=react)
    payload = r.json()
    assert payload["message"] == "<p>Invalid react ID</p>"
    assert payload["code"] == 400

def test_http_message_react_positive_react_id(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    react = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 10000
    }

    r = requests.post(url + "message/react", json=react)
    payload = r.json()
    assert payload["message"] == "<p>Invalid react ID</p>"
    assert payload["code"] == 400

def test_http_message_react_negative_react_id(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    react = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": -10000
    }

    r = requests.post(url + "message/react", json=react)
    payload = r.json()
    assert payload["message"] == "<p>Invalid react ID</p>"
    assert payload["code"] == 400

def test_http_message_react_already_reacted(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    react = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 1
    }

    requests.post(url + "message/react", json=react)
    r = requests.post(url + "message/react", json=react)
    payload = r.json()
    assert payload["message"] == "<p>User has already reacted to this message</p>"
    assert payload["code"] == 400

# Tests for message_unreact

def test_http_message_unreact_message_does_not_exist(url):
    clear()
    login_owner = reg_owner(url)
    create_unique_channel(url, login_owner, "channel", True)

    unreact = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 1
    }

    r = requests.post(url + "message/unreact", json=unreact)
    payload = r.json()
    assert payload["message"] == "<p>Specified message does not exist</p>"
    assert payload["code"] == 400

def test_http_message_unreact_removed_message(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")
    
    remove = {
        "token": login_owner["token"],
        "message_id": 0
    }

    requests.delete(url + "message/remove", json=remove)

    unreact = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 1
    }

    r = requests.post(url + "message/unreact", json=unreact)
    payload = r.json()
    assert payload["message"] == "<p>Specified message does not exist</p>"
    assert payload["code"] == 400

def test_http_unreact_message_in_private_channel(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", False)
    login_user = reg_user(url)

    msg_send(url, login_owner, channel_id, "example_message")

    unreact = {
        "token": login_user["token"],
        "message_id": 0,
        "react_id": 1
    }

    r = requests.post(url + "message/unreact", json=unreact)
    payload = r.json()
    assert payload["message"] == "<p>User is not currently in the channel of the message they are trying to react to</p>"
    assert payload["code"] == 400

def test_http_message_unreact_react_id_0(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    unreact = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 0
    }

    r = requests.post(url + "message/unreact", json=unreact)
    payload = r.json()
    assert payload["message"] == "<p>Invalid react ID</p>"
    assert payload["code"] == 400   

def test_http_message_unreact_positive_react_id(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    unreact = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 10000
    }

    r = requests.post(url + "message/unreact", json=unreact)
    payload = r.json()
    assert payload["message"] == "<p>Invalid react ID</p>"
    assert payload["code"] == 400

def test_http_message_unreact_negative_react_id(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    unreact = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": -10000
    }

    r = requests.post(url + "message/unreact", json=unreact)
    payload = r.json()
    assert payload["message"] == "<p>Invalid react ID</p>"
    assert payload["code"] == 400

def test_http_message_unreact_message_has_no_reacts(url):
    clear()
    login_owner = reg_owner(url)
    channel_id = create_unique_channel(url, login_owner, "channel", True)

    msg_send(url, login_owner, channel_id, "example_message")

    unreact = {
        "token": login_owner["token"],
        "message_id": 0,
        "react_id": 1
    }

    r = requests.post(url + "message/unreact", json=unreact)
    payload = r.json()
    assert payload["message"] == "<p>User has not reacted to this message yet</p>"
    assert payload["code"] == 400

    