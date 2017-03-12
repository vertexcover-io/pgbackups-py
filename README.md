# pybackups-py

[<img src="https://img.shields.io/pypi/v/pgbackups-py.svg">](https://pypi.python.org/pypi/pgbackups-py)

A python port of [pgbackups-archive](https://github.com/kjohnston/pgbackups-archive)
that helps in automating Heroku PGBackups and archiving them to Amazon S3.

# Overview

This package provides a python script `pgbackups` that will capture a Heroku 
PGBackup, wait for it to complete, and then store it within the Amazon S3 bucket
you specify. Best way to use this package is to use heroku scheduler to schedule 
this python script at any required durations and get automated offsite backups.
This project though can also be used as a library and can be used within
your own code. The `pgbackups` script can also be run 
from command line to generate adhoc backups


This package doesn't interfere with or utilze automated backups, so feel free to 
schedule those with the `pg:backups schedule` command as you desire.

# Installation

    pip install -e pgbackups-py

# Usage

To use it with heroku scheduler:

#### Install Heroku Scheduler add-on

    heroku addons:create scheduler

Setup an AWS IAM user, S3 bucket and policy
A good security measure would be to use a dedicated set of AWS credentials with 
a security policy only allowing access to the bucket you're specifying. See this 
Pro Tip on Assigning an AWS IAM user access to a single S3 bucket.

#### Configure Backups

The backups can either be configured by setting environment variables or by 
passing arguments to the provided `pgbackups` script. On heroku environemnt 
variables can be set as below  

    # Required
    heroku config:add HEROKU_API_KEY="collaborator-api-key"
    heroku config:add PGBACKUPS_APP="myapp"
    heroku config:add PGBACKUPS_AWS_ACCESS_KEY_ID="XXX"
    heroku config:add PGBACKUPS_AWS_SECRET_ACCESS_KEY="YYY"
    heroku config:add PGBACKUPS_BUCKET="myapp-backups"    

    # Optional: If you wish to backup a database other than the one that
    # DATABASE_URL points to, set this to the name of the variable for that
    # database (useful for follower databases).
    heroku config:add PGBACKUPS_DATABASE="HEROKU_POSTGRESQL_BLACK_URL"
    
The `pgbackups` script takes following options

      -h, --help            show this help message and exit
      --app APP             Heroku App for which backup needs to be performed
      --api-key API_KEY     API key for heroku
      --db DB_NAME          Name of Heroku database
      --access-key ACCESS_KEY
                            AWS Access Key
      --secret-key SECRET_KEY
                            AWS SECRET Key
      --aws-bucket AWS_BUCKET
                            AWS S3 Bucket
      --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Log Level
      --disable-logging     Enable Logging
      --log-name LOG_NAME   Log Name
      --storage-opts [STORAGE_OPTIONS [STORAGE_OPTIONS ...]]
                            set additional storage options as key=value
      --delete-after        Delete backups from heroku after storing to s3

####Add the backup task to scheduler

    heroku addons:open scheduler

Then specify `pgbackups` as a command you would like to run at any of the available intervals.


## License

* MIT license.