# pybackups-py

A python port of [pgbackups-archive](https://github.com/kjohnston/pgbackups-archive)
that helps in automating Heroku PGBackups and archiving them to Amazon S3.

# Overview

This package provides an [invoke](http://www.pyinvoke.org/index.html)
task that will capture a Heroku PGBackup, wait for it to complete,
and then store it within the Amazon S3 bucket you specify. Best way
to use this package is to use heroku scheduler to schedule this invoke
task at any required durations and get automated offsite backups.
This project though can also be used as a library within your own
invoke task or any other piece of code


This package doesn't interfere with or utilze automated backups,
so feel free to schedule those with the pg:backups schedule command as you desire.

# Installation

    pip install -e <>

# Usage

To use it with heroku scheduler:

#### Install Heroku Scheduler add-on

    heroku addons:create scheduler

Setup an AWS IAM user, S3 bucket and policy
A good security measure would be to use a dedicated set of AWS credentials with a security policy only allowing access to the bucket you're specifying. See this Pro Tip on Assigning an AWS IAM user access to a single S3 bucket.

#### Apply Environment Variables

    # Required
    heroku config:add HEROKU_API_KEY="collaborator-api-key"
    heroku config:add PGBACKUPS_APP="myapp"
    heroku config:add PGBACKUPS_AWS_ACCESS_KEY_ID="XXX"
    heroku config:add PGBACKUPS_AWS_SECRET_ACCESS_KEY="YYY"
    heroku config:add PGBACKUPS_BUCKET="myapp-backups"
    heroku config:add PGBACKUPS_REGION="us-west-2"


    # Optional: If you wish to backup a database other than the one that
    # DATABASE_URL points to, set this to the name of the variable for that
    # database (useful for follower databases).
    heroku config:add PGBACKUPS_DATABASE="HEROKU_POSTGRESQL_BLACK_URL"

####Add the invoke task to scheduler

    heroku addons:open scheduler

Then specify `invoke pgbackups.capture` as a task you would like to run at any of the available intervals.


To use it as a library

\#TODO:

## License

* MIT license.