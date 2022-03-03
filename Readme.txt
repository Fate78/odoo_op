INTRODUCTION
----------------------------------------------------------------------------------------------

The openproject Odoo module syncs the data between odoo and openproject,
using the openproject api to transfer its data to odoo's database.

It also has the function of creating automated tasks given a frequency and an interval.

REQUIREMENTS
----------------------------------------------------------------------------------------------

This module doesn't require any other specific modules


INSTALLATION
----------------------------------------------------------------------------------------------

https://github.com/Fate78/openproject.git

1. Clone the repository into a custom addons folder
2. Run odoo including your custom folder in the command as well as the database as seen below
    
    ./odoo-bin --addons-path=~/odoo/addons,~/odoo-custom-addons -d odoo_db

3. In the Apps menu install the 'openproject' module


CONFIGURATION
----------------------------------------------------------------------------------------------

Insert the API Key into the modules settings:
1. Copy the API key from OpenProject
    a)My Account->Access token-> API
2. Add the key to the Odoo Module
    a)Home Menu->Settings->Open Project
    b)Paste the API key into the text field and save


CUSTOMIZATION
----------------------------------------------------------------------------------------------

#TODO
Variable to customize the interval of time in which the program will look for updates
Add a variable for the due date of the task -> Integer (ex. field due_in=4 -> due_date=now + 4 days)


Scheduled Tasks:
----------------------------------------------------------------------------------------------

In the schedule's menu it's possible to add daily, weekly and monthly tasks that will be created in a given interval of time
An interval of 2 = every 2 days, 2 weeks or 2 months depending on the given frequency.

run_today = True, if you want the start date to be today