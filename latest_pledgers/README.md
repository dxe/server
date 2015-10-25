#Latest Pledgers
This endpoint basically just uses Google's API to query the spreadsheet
behind [The Liberation Pledge](http://liberationpledge.com/) form and
returns the last N of the results, filtering out the private/unnecessary fields.

##How to use it
Example request:

```
GET http://dxetech.org/pledge/latest_pledgers/10
```

See the Facebook Data [example_request.html](example_request.html) for an
example of how to make a request to this endpoint from JavaScript without
JQuery.

See [latest_pledgers.py](latest_pledgers.py) for the full functionality.

##Why this is a thing
We can't put the credentials to access the spreadsheet in JavaScript because
then anyone can access it, so we have to proxy the request through our server.
NBD.


##Setting Up The Google Spreadsheets API
###Get Credentials
This comes from [here](https://pip.pypa.io/en/latest/installing.html).

1. Visit https://console.developers.google.com/project
1. Create a project.
1. On the left bar navigate to 'APIs & auth' > 'APIs' > 'Drive API'
1. Click 'Enable API'
1. On the left bar navigate to 'APIs & auth' > 'APIs' > 'Credentials'
1. Click 'Add Credentials', select 'Service Account', json filetype, and 'Create'
   You'll then download a json file containing the credentials.

###Give API Access To Spreadsheets
In order for the to actually access the specific spreadsheet, you have to give
permissions in the same way you would give a user access to a spreadsheet.
Go to the spreadsheet, on the top right click 'Share', and enter
the email address found under `client_email` in the api credentials
file you just downloaded.

###Full Spreadsheets API
A python libaray wrapping the [Google Sheets
API](https://developers.google.com/google-apps/spreadsheets/?hl=en) for
interfacing with spreadsheets is [gspread](https://github.com/burnash/gspread).

The documentation is [here on readthedocs](http://gspread.readthedocs.org/en/latest/index.html).
One important detail about the API is that all cells are returned as strings
despite the underlying spreadsheet cell format.
