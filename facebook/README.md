#Facebook Data API
**NOTE:** This is currently not being used anywhere (12/13/15).


This endpoint basically just hits the [Facebook Graph
API](https://developers.facebook.com/docs/graph-api) and returns
the results.

##How to use it

Example request:
```
GET http://dxetech.org/facebook/attending_event?event_id=1697430973810357
```

See [example_request.html](example_request.html) for an example in JavaScript without JQuery.

See [facebook.py](facebook.py) for the full functionality.

##Why this is a thing
Why can't we just directly hit the graph api instead of going
through this proxy? Good question, you're so clever. The reason is that all
Graph requests need to come with an [access
token](https://developers.facebook.com/docs/facebook-login/access-tokens/). The
User Access token requires a user to log in to make the request. The App Access
token can't be visible to clients (like JavaScript). The Page Access token are
for managing Pages. It's hard to find info on Client Tokens, but I don't think
it works here.

##How to set it up
Become a Facebook Developer [here](https://developers.facebook.com/apps) and
then create a new app. The platform for the app is "Website". Go through the
steps and do whatever's reasonable. Then go to the deashboard for the app. At
the dashboard you'll see the App ID and App Secret. Hit their [oauth
API](https://developers.facebook.com/docs/facebook-login/access-tokens#apptokens)
to get an `access_token`:

```
curl "https://graph.facebook.com/oauth/access_token\
?client_secret=<client secret>\
&client_id=<client id>\
&grant_type=client_credentials"
```

With that, you can ask the Facebook Graph API for things by making the request
with the request header:

```
Authorization: Bearer <access token>
```

Don't let anyone get this access key. Put it in [config/facebook.sh](http://github.com/directactioneverywhere/config/blob/master/facebook.sh) as:

```
export FACEBOOK_APP_ACCESS_TOKEN="<access token>"
```

Finally, go through their [App Security
Checkup](https://developers.facebook.com/tools/app-security-checkup/) and make
everything as unpermissive as possible and convenient while things still work.
