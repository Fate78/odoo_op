from requests.models import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import hashlib
from base64 import b64encode
from pprint import pprint
from datetime import datetime
from dateutil import parser
import time

class PostProjects(models.TransientModel):
    _name = 'test.script'
    _description = 'Test Script'

    def cron_test(self):
        for i in range(0,50):
            print(i)
            time.sleep(1)

    # Time_cpu=10
    # Time_real=20
    # Cron=-1
    # Timeout ao fim de 20seg

    # Time_cpu=10
    # Time_real=20
    # Cron=10
    # Timeout ao fim de 10seg - cron continua
    # Timeout ao fim de 20seg

    # Time_cpu=10
    # Time_real=20
    # Cron=10
    # workers=0
    # No Timeout

