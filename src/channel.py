from data import data
from error import AccessError, InputError
def channel_invite(token, channel_id, u_id):
    global data
    channel_id_true = False
    for channel_invited in data['channels']:
        if channel_invited['channel_id'] == channel_id:
            channel_id_true = True
            break   
    if channel_id_true == False:
        raise InputError("Invalid channel id")

    token_exist = False
    for inviter in data['users']:
        if inviter['token'] == token:
            token_exist = True
            break
    if token_exist == False:
        raise AccessError("Token does not exist")

    token_true = False
    for members in channel_invited['all_members']:
        if inviter['u_id'] == members['u_id']:
            token_true = True
            break
    if token_true == False:
        raise AccessError("Inviter is not part of this channel")

    for members in channel_invited['all_members']:
        if members['u_id'] == u_id:
            raise InputError("Invitee is already invited to this channel")

    u_id_true = False
    for invitee in data['users']:
        if invitee['u_id'] == u_id:
            u_id_true = True
            break
    if u_id_true == False:
        raise InputError("Invitee does not exist")

    invitee_member_info = {'u_id' : invitee['u_id'], 'name_first' : invitee['name_first'], 'name_last' : invitee['name_last']}
    channel_invited['all_members'].append(invitee_member_info)

    return {}

def channel_details(token, channel_id):
    channel_id_true = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            channel_id_true = True
            break   
    if channel_id_true == False:
        raise InputError("Invalid channel id")

    token_exist = False
    for user in data['users']:
        if user['token'] == token:
            token_exist = True
            break
    if token_exist == False:
        raise AccessError("Token does not exist")

    token_true = False
    for members in channel['all_members']:
        if user['u_id'] == members['u_id']:
            token_true = True
            break
    if token_true == False:
        raise AccessError("Authorised user is not part of this channel")

    channel_details_dict = {'name' : channel['name'], 'owner_members' : channel['owner_members'], 'all_members' : channel['all_members']}

    return channel_details_dict

def channel_messages(token, channel_id, start):
    global data
    # Check channel_id
    num_users = len(data["users"])
    num_channels = len(data["channels"])
    u_id = 0
    for x in range(num_users):
        if data["users"][x]["token"] == token:
            u_id = data["users"][x]["u_id"]
    correct_channel_id = False
    isValid_token = False
    channel_index = -1

    for x in range(num_channels):
        if data["channels"][x]["channel_id"] == channel_id:
            correct_channel_id = True
            channel_index = x
            # Check token
            num_members = len(data["channels"][x]["all_members"])
            for i in range(num_members):
                if u_id in data["channels"][x]["all_members"][i]["u_id"]:
                    isValid_token = True
                    break
            break
    if correct_channel_id == False:
        raise InputError("Channel ID is not a valid channel")
    if isValid_token == False:
        raise AccessError("Authorised user is not a member of channel with channel_id")
    # Check whether start > no. messages in channel
    if  start > len(data["channels"][channel_index]["messages"]):
        raise   InputError("Start is greater than the total number of messages in the channel")
    
    # Initialise return dictionary
    returnDict = {}
    returnDict["messages"] = []
    returnDict["start"] = start
    returnDict["end"] = 50
    num_messages = 50
    if len(data["channels"][channel_index]["messages"]) <= 50:
        returnDict["end"] = -1
        num_messages = len(data["channels"][channel_index]["messages"])
    for x in range(num_messages):
        returnDict["messages"].append(data["channels"][channel_index]["messages"][x])
    return returnDict

def channel_leave(token, channel_id):
    global data
    # Check channel_id
    num_users = len(data["users"])
    num_channels = len(data["channels"])
    u_id = 0
    for x in range(num_users):
        if data["users"][x]["token"] == token:
            u_id = data["users"][x]["u_id"]
    correct_channel_id = False
    isValid_token = False
    channel_index = -1
    member_index = -1

    for x in range(num_channels):
        if data["channels"][x]["channel_id"] == channel_id:
            correct_channel_id = True
            channel_index = x
        # Check token
        num_members = len(data["channels"][x]["all_members"])
        for i in range(num_members):
            if data["channels"][x]["all_members"][i]["u_id"] == u_id:
                member_index = i
                isValid_token = True
                    
    if isValid_token == False:
        raise AccessError("Authorised user is not a member of channel with channel_id")
    if correct_channel_id == False:
        raise InputError("Channel ID is not a valid channel")
    
    # Check if user is an owner_member
    num_owners = len(data["channels"][channel_index]["owner_members"])
    for owner_index in range(num_owners):
        if data["channels"][channel_index]["owner_members"][owner_index]["u_id"] == u_id:
            remove_target = data["channels"][channel_index]["owner_members"][owner_index]
            data["channels"][channel_index]["owner_members"].remove(remove_target)
            break
    # Remove member
    remove_target = data["channels"][channel_index]["all_members"][member_index]
    data["channels"][channel_index]["all_members"].remove(remove_target)
    # Check if channel still has members
    if len(data["channels"][channel_index]["all_members"]) == 0:
        data["channels"].remove(data["channels"][channel_index])
    return {}

def channel_join(token, channel_id):
    global data
    # Check channel id
    num_channels = len(data["channels"])
    isChannelPublic = True
    correct_channel_id = False
    channel_index = -1
    for x in range(num_channels):
        if data["channels"][x]["channel_id"] == channel_id:
            correct_channel_id = True
            channel_index = x
            # Check if the channel is private
            if data["channels"][x]["is_public"] == False:
                isChannelPublic = False
                break
            break

    if correct_channel_id == False:
        raise InputError("Channel ID is not a valid channel")
    if isChannelPublic == False:
        raise AccessError("Channel is private")
    # Add user to channel
    num_users = len(data["users"])
    user_dictionary = {}
    for x in range(num_users):
        if data["users"][x]["token"] == token:
            user_dictionary["u_id"] = data["users"][x]['u_id']
            user_dictionary["name_first"] = data["users"][x]['name_first']
            user_dictionary["name_last"] = data["users"][x]['name_last']
            break
    data["channels"][channel_index]["all_members"].append(user_dictionary)
    return {}

def channel_addowner(token, channel_id, u_id):
    global data

    channel_id_true = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            channel_id_true = True
            break   
    if channel_id_true == False:
        raise InputError("Invalid channel id")

    token_exist = False
    for user in data['users']:
        if user['token'] == token:
            token_exist = True
            break
    if token_exist == False:
        raise AccessError("Token does not exist")

    token_true = False
    for members in channel['owner_members']:
        if user['u_id'] == members['u_id']:
            token_true = True
            break
    if token_true == False:
        raise AccessError("Authorised user is not an owner")
   
    for members in channel['owner_members']:
        if members['u_id'] == u_id:
            raise InputError("User is already an owner of this channel")

    u_id_true = False
    for member in channel['all_members']:
        if member['u_id'] == u_id:
            u_id_true = True
            break
    if u_id_true == False:
        raise InputError("User is not part of the channel")

    member_info = {'u_id' : member['u_id'], 'name_first' : member['name_first'], 'name_last' : member['name_last']}
    channel['owner_members'].append(member_info)

    return {}

def channel_removeowner(token, channel_id, u_id):
    global data

    channel_id_true = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            channel_id_true = True
            break   
    if channel_id_true == False:
        raise InputError("Invalid channel id")

    token_exist = False
    for user in data['users']:
        if user['token'] == token:
            token_exist = True
            break
    if token_exist == False:
        raise AccessError("Token does not exist")

    token_true = False
    for members in channel['owner_members']:
        if user['u_id'] == members['u_id']:
            token_true = True
            break
    if token_true == False:
        raise AccessError("Authorised user is not an owner")
    
    is_owner = False
    for member in channel['owner_members']:
        if member['u_id'] == u_id:
            is_owner = True
            break
    if is_owner == False:
        raise InputError("User is not an owner of this channel")

    channel['owner_members'].remove(member)

    return {}