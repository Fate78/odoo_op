from pdb import post_mortem
from requests.models import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta

"""Este cron vais percorrer o model das Scheduled tasks e verificar se existem daily tasks
    Caso existam daily tasks vai adicioná-las ao OpenProject"""
class PostWorkPackages(models.AbstractModel):
    _name = 'check.schedules'
    _description = 'Check Schedules'
    limit=10

    def generator(self,data):
        yield data

    def post_work_package(self, project_id, responsible_id, main_url, name, description, start_date, due_date):
        env = self.env['op.work.package']
        response = env.post_response(main_url, env.get_payload(project_id, responsible_id, name, description,start_date, due_date))

    def post_daily_task(self,name,description):
        env_wp = self.env['op.work.package']
        projects_page_url = env_wp.get_projects_url()
        response = env_wp.get_response(projects_page_url)
        page_size = response['total']
        response = self.env['op.project'].get_response(projects_page_url + "?filters=[]&offset=1&pageSize=%s" % (page_size))

        wp_ref = datetime.now().strftime("%Y-%m-%d")
        start_date = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        wp_name = name + "_" + wp_ref
        is_admin=None
        admin_id=None
        #Get project members
        for r in response['_embedded']['elements']:
            project_id = r['id']

            if(r['active']!=False):
                project_url_gen = self.generator(env_wp.get_project_url(project_id))
                post_wp_url_gen = self.generator(env_wp.get_project_workpackages_url(project_id))
            for p_url in project_url_gen:
                response_project_gen = self.generator(env_wp.get_response(p_url))
                print("Projects: ", p_url)
            for rp in response_project_gen:
                memberships_href_gen = self.generator(env_wp.base_path + rp['_links']['memberships']['href'])
            for m_url in memberships_href_gen:
                response_members_gen = self.generator(env_wp.get_response(m_url))
                print("Memberships: ", m_url)

            for u in response_members_gen:
                for i in u['_embedded']['elements']:
                    user_id = env_wp.get_id_href(i['_links']['principal']['href'])
                    for r in i['_links']['roles']:
                        role_id = env_wp.get_id_href(r['href'])
                        if(role_id=="3"):
                            is_admin=True
                            admin_id=user_id
            for url in post_wp_url_gen:
                print("post_wp:",url)
                # if(is_admin==True):
                #     post_work_package = env_wp.post_response(url, env_wp.get_payload(project_id, admin_id, wp_name, description, start_date, due_date))
                #     print(post_work_package)       
                # else:
                #     post_work_package = env_wp.post_response(url, env_wp.get_payload(project_id, user_id, wp_name, description, start_date, due_date))
                #     print(post_work_package)   

    def cron_check_scheduled_tasks(self):
        env_s_tasks = self.env['op.scheduled.tasks']
        tasks = env_s_tasks.get_data(self.limit)
        for t in tasks:
            t_name = t.name
            t_frequency = t.frequency
            t_description = env_s_tasks.verify_field_empty(t.description)
            
            if(t_frequency=="daily"):
                self.post_daily_task(t_name, t_description)