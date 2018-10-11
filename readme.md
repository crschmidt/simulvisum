# simulvisum

simulvisum is a tool to allow people to watch YouTube together. It acts as
a service providing a minimal chat alongside a shared YouTube playlist (synced
with other viewers).

Other similar projects:

 - watch2gether.com
 - https://sync-video.com/
 - https://letsgaze.com/

## Credentials

You will need credentials for Pusher (https://pusher.com/) and for Google's APIs (console.developers.google.com) with YouTube services enabled.

Pusher credentials should be placed in the simulvisum/settings.py file.

## Setup

- Create a virtualenv, and install the necessary requirements.
- Create a client_secrets.json file for Google API keys: You can find it in the Google developer console. https://console.developers.google.com/apis/credentials- Run main/playlist.py --noauth_local_webserver to create a set of oauth credentials.
- Create a superuser with `python manage.py createsuperuser
- Run python manage.py runserver
- Access http://localhost:8000/admin/, and create a "Lounge" object with the playlist you want to use.
- Access http://localhost:8000/1/

This is not an officially supported Google product.
