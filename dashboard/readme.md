# DB

## Initial Setup

Run these commands to start up the database. It assumes you have
`AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY` set in your environment.

```
source ../config/dbpw.sh
terraform apply
```

Then read the output, and copy the dbstring. Then run this to create the database
schema:

```
psql -f db_setup.sql "<dbstring>"
```

Yay!
