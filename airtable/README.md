# Airtable Backup

Backs up the Airtable data to S3.

##How To Inspect The Airtable Backups

###Access

The backups are stored in Amazon's S3 storage service. The access credentials
are in
[config/airtable.sh](https://github.com/directactioneverywhere/config/blob/master/airtable.sh).
Install the [AWS
CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html), probably
just by running `pip install awscli`. Then run `aws configure` to set the access credentials (do defaults for the other options).

Then you can list all of the airtable backups by running:

```
aws s3 ls s3://dxe-backup/airtable/
```

It will output a bunch, all timestamped. Probably grab the one at the bottom, the most recent one. Copy the file name to paste into this command:

```
mkdir backup
aws s3 cp s3://dxe-backup/airtable/<pasted file name> backup/
```

###Parsing it
Yay, you downloaded a backup. Unzip it:

```
cd backup/
unzip <pasted file name>
```

Now you'll see a few json files, each of which represent a data dump of a different table in the base. The contents of each are structured like:

```json
[ {
      "createdTime": "2015-11-12T01:39:30.000Z",
      "fields": {
         "column1": "row1col1 value",
         "column2": 2,
         ...
      },
      "id": "recvTwBkAt1ThX0ZL"
   },
   ...
]
```

The only thing interesting is that sometimes values will be these weird strings
like "recvTwBkAt1ThX0Z". These are references (by id) to other records. For example, each row in "All Members" has a value in the "chapter_id" column that points to a record in the "Chapters" table.

We haven't built anything to help code handle those references because we haven't needed to yet. If you're reading this any about to do that, have fun mate, that doesn't sound like fun.


# Airtable To Mailing List Sync

Syncs the Google Groups mailing lists members one-way from Airtable. As each member is added to the Google Group for the first time, the chapter whose mailing list they were added to is recorded in the Airtable. The member will not be added again, even if they are removed from the Google Group. This is so that the members can unsubscribe themselves from the Google Group without us having to use heuristics to figure out whether they unsubscribed or just weren't added.

## Run

To sync the Google Groups Mailing Lists from the data in Airtable, run:

```bash
$ make sync
```

## Setup

You need a client_secret.json to authenticate with Google user with the following scopes: "https://www.googleapis.com/auth/admin.directory.group", "https://www.googleapis.com/auth/admin.directory.group.member".

You also need AIRTABLE_API_KEY set in your env.

## Test

```bash
$ make test-sync
```
