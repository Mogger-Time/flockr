# COMP1531 Major Project Assumptions

## Auth
* The u_id returned from auth_register and auth_login should match when logging in with the same details which have just been registered with.
* Space bars are considered characters for password length.
* First and last name contain no spaces may contain symbols such as !@#$%^&*(
* Registering will login the user.
* The token returned from auth_register and auth_login will be the same as the user email.
* u_id is a positive number (>= 1).
* For the auth_login function to work there must be at least one registered user.

## Channel
* The channel_details function returns a dictionary
* Users will be able to see public channels, and can join them (channel_join)
* Users invited to a channel do not need to join them after
* channel_id is a positive number (>= 1)
* If the last member of a channel leaves, all the data for that channel is deleted

## Channels
* The name of a new channel can include space bars (considered as characters) and symbols.
* The names of new channels can be the same as existing channels.
* The channel will not be able to be created with an empty name.
