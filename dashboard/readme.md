## Dashboard

The dashboard is an attempt to provide metrics on how DxE is doing. Currently,
this means pulling data from the Facebook Graph API into a postgresql db, and
generating csvs from that data, exposing that data on the server to be graphed
<somewhere>.

Here is the data currently being exposed:
* [Monthly event attendee counts](dxetech.org/dashboard/monthly_attendees.csv)

## DB Setup

This is how to set up the db from scratch. This isn't likely to be necessary often.

Run these commands to start up the database. It assumes you have
`AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY` set in your environment.

```
source ../config/db.sh
terraform apply
```

Then read the output, and copy the dbstring. Then run this to create the database
schema:

```
psql -f db_setup.sql "<dbstring>"
```

Also update `config/db.sh` to expose the connection info to code that needs it:

```
export DB_STRING="<dbstring>"
```

Yay!
