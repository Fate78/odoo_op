INTRODUCTION
----------------------------------------------------------------------------------------------

The openproject Odoo module syncs the data between odoo and openproject,
using the openproject api to transfer its data to odoos database. 


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
3. 


COSTUMIZATION
----------------------------------------------------------------------------------------------

#TODO
Variable to costumize the interval of time in which the program will look for updates
