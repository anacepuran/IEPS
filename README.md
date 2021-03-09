# IEPS project

The following project is the implementation of the multi threaded web crawler developed in Python.

Additional libraries included: bs4, psycopg2, hyperlink

POSTGRESQL SETUP:

1. Install postgresql (in the process you will be prompted to choose the password - I recommend "postgres")
2. Open SQL shell
3. Login with default values (port, host, name, ...) and enter the password chosen in the installation process (postgres)
4. Run the following commands: <br/>
   CREATE DATABASE spider; ... which creates the db <br/>
   \c spider ... which connects to the db <br/>
   \i 'path to the crawldb.sql file downloaded from moodle' ... which runs the script and initiates the db values
5. Now your local db should be set. Open the pgAdmin 4 web app (which was also installed with the shell and postgresql) and check whether the database was initiated correctly. Under schemas there should be one named crawldb!
