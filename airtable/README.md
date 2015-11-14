# Airtable Backup

Backs up the Airtable data to S3.

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
