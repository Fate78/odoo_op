from requests.models import HTTPBasicAuth
from odoo import models, fields, api
import requests
import json
from base64 import b64encode
from pprint import pprint

class SyncWizard(models.TransientModel):
    _name = 'sync.wizard'
    base_path = "http://localhost:8080"
    endpoint_url = "/api/v3/projects/3/work_packages"

    main_url = "%s%s" % (base_path, endpoint_url)
    def get_response(url):
        api_key = '815d740a36b1236c4235a22196bc2d79e44d1fbd5e756e29534efb0b6c1f6639'
        base_path = "http://localhost:8080"
        endpoint_url = "/api/v3/projects/3/work_packages"
        filter_url = "?filters=[{\"startDate\":{\"operator\":\"<>d\",\"values\":[\"2021-11-22\",\"2021-11-24\"]}}]"

        main_url = "%s%s%s&pageSize=100" % (base_path, endpoint_url, filter_url)
        resp = requests.get(
            main_url,
            auth=('apikey', api_key)
            )
        return json.loads(resp.text)

    response = get_response(main_url)

    print(response['_links']['self']['href'])
    for r in response['_embedded']['elements']:
        print(r['id'])
        print (r['spentTime'])
    response = get_response(main_url)


    def btn_sync(self):
        notification = {
        'type': 'ir.actions.client',
        'tag': 'display_notification', 
        'params': {
            'title': ('Notice'),
            'message': 'To be implemented',
            'type':'warning',  #types: success,warning,danger,info
            'sticky': False,  #True/False will display for few seconds if false
        }}
        return notification

    # def cron_sync(self):
        # self.env.cr.execute("SELECT * FROM op_project")
        # values = self.env.cr.dictfetchall()
        # for index in range(0, len(values)):
        #     print(f"\n\n {values[index]} \n\n")
        # self.env.cr.execute("""UPDATE op_project
        #                     SET name=%s, public=%s, partner_id=%d, billable=%d, default_rate=%2.2f, responsible_id=%d, currency_id=%d, op_activity_ids=%d
        #                     WHERE op_identifier=%d
        #                     RETURNING op_identifier""",
        #                  ())
        
        # headers={'x-api-key':'815d740a36b1236c4235a22196bc2d79e44d1fbd5e756e29534efb0b6c1f6639'}
        # try:   
        #     response = requests.get('http://localhost:8080/projects/your-scrum-project/work_packages', headers=headers)
        #     print(response)
        # except:
        #     print("Exception ocurred")