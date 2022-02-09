from pdb import post_mortem
from requests.models import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
import hashlib
import json

"""Este cron vais percorrer o model das Scheduled tasks e verificar se existem daily tasks
    Caso existam daily tasks vai adicioná-las ao OpenProject"""
class PostWorkPackages(models.AbstractModel):
    _name = 'check.schedules'
    _description = 'Check Schedules'
    limit=20

    def get_hashed(self, project_id, name, responsible_id):
        env_wp = self.env['op.work.package']
    
        project_id = env_wp.verify_field_empty(project_id)
        name = env_wp.verify_field_empty(name)
        responsible_id = env_wp.verify_field_empty(responsible_id)
        print(project_id, name, responsible_id)
        hashable = json.dumps(project_id) + name + responsible_id
        hashed = hashlib.md5(hashable.encode("utf-8")).hexdigest()
        return hashed

    def generator(self,data):
        yield data

    def post_work_package(self, project_id, responsible_id, main_url, name, description, start_date, due_date):
        env = self.env['op.work.package']
        response = env.post_response(main_url, env.get_payload(project_id, responsible_id, name, description,start_date, due_date))

    def get_response_members_gen(self):
        env_wp = self.env['op.work.package']
        projects_page_url = env_wp.get_projects_url()
        response = env_wp.get_response(projects_page_url)
        next_offset_project = True

        while next_offset_project:
            #Get project members
            for r in response['_embedded']['elements']:
                project_id = r['id']
                if(r['active']!=False):
                    project_url_gen = self.generator(env_wp.get_project_url(project_id))
                    post_wp_url_gen = self.generator(env_wp.get_project_workpackages_url(project_id))
                for p_url in project_url_gen:
                    response_project_gen = self.generator(env_wp.get_response(p_url))
                for rp in response_project_gen:
                    memberships_href_gen = self.generator(env_wp.base_path + rp['_links']['memberships']['href'])
                for m_url in memberships_href_gen:
                    response_members_gen = self.generator(env_wp.get_response(m_url))
            next_offset_project, response = env_wp.check_next_offset(next_offset_project, response)
            
            return response_members_gen, post_wp_url_gen

    def post_daily_task(self,name,description):
        env_wp = self.env['op.work.package']
        projects_page_url = env_wp.get_projects_url()
        response = env_wp.get_response(projects_page_url)
        wp_page_url = env_wp.get_workpackages_url()
        response_work_package = env_wp.get_response(wp_page_url)

        wp_ref = datetime.now().strftime("%Y-%m-%d")
        start_date = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        wp_name = name + "_" + wp_ref
        is_admin=None
        admin_id=None
        
        next_offset_wp = True
        next_offset_memb = True

        response_members_gen, post_wp_url_gen = self.get_response_members_gen()

        for u in response_members_gen:
            while next_offset_memb:
                for i in u['_embedded']['elements']:
                    user_id = env_wp.get_id_href(i['_links']['principal']['href'])
                    project_id = env_wp.get_id_href(i['_links']['project']['href'])
                    for r in i['_links']['roles']:
                        role_id = env_wp.get_id_href(r['href'])
                        if(role_id=="3"):
                            is_admin=True
                            admin_id=user_id
                            print("admin id: ", admin_id)
                    print("\n",i)

                    while next_offset_wp:
                        for rw in response_work_package['_embedded']['elements']:
                            _name = rw['subject']
                            _id_project = env_wp.get_id_href(rw['_links']['project']['href'])
                            _responsible = env_wp.get_id_href(rw['_links']['responsible']['href'])
                            hashed_op = self.get_hashed(_id_project, _name, _responsible)
                            hashed_new = self.get_hashed(project_id, wp_ref, admin_id)
                        if(hashed_op!=hashed_new):  
                            for url in post_wp_url_gen:
                                print("post_wp:",url)
                                if(is_admin==True):
                                    post_work_package = env_wp.post_response(url, env_wp.get_payload(project_id, admin_id, wp_name, description, start_date, due_date))
                                    print("Posting WP: ", hashed_new)       
                                else:
                                    print("The Project needs a project admin")
                        next_offset_wp, response_work_package = env_wp.check_next_offset(next_offset_wp, response_work_package)
                next_offset_memb, response = env_wp.check_next_offset(next_offset_memb, response)
    
    def cron_check_scheduled_tasks(self):
        env_s_tasks = self.env['op.scheduled.tasks']
        tasks = env_s_tasks.get_data(self.limit)
        for t in tasks:
            t_name = t.name
            t_frequency = t.frequency
            t_description = env_s_tasks.verify_field_empty(t.description)
            
            if(t_frequency=="daily"):
                self.post_daily_task(t_name, t_description)