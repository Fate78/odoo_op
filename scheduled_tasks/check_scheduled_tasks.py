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

    def post_work_package(self, project_id, main_url, name):
        response = self.post_response(main_url, self.get_payload(project_id, name))

    def post_daily_task(self,name,description):
        env_wp = self.env['op.work.package']
        projects_page_url = env_wp.get_projects_url()
        response = env_wp.get_response(projects_page_url)

        wp_ref = datetime.now().strftime("%Y-%m-%d")
        start_date = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        wp_name = name + "_" + wp_ref

        #Get project members
        for r in response['_embedded']['elements']:
            project_id = r['id']

            if(r['active']!=False):
                project_url_gen = self.generator(env_wp.get_project_url(project_id))
                post_wp_url_gen = self.generator(env_wp.get_project_workpackages_url(project_id))
                print("added p_url and wp_url with p: ", project_id)
            for p_url in project_url_gen:
                response_project_gen = self.generator(env_wp.get_response(p_url))
            for rp in response_project_gen:
                memberships_href_gen = self.generator(env_wp.base_path + rp['_links']['memberships']['href'])
            for m_url in memberships_href_gen:
                response_members_gen = self.generator(env_wp.get_response(m_url))
                
                
            print("------Members of Project-------")
            for u in response_members_gen:
                if(u['count']>0):
                    for i in u['_embedded']['elements']:
                        user_id_gen = self.generator(env_wp.get_id_href(i['_links']['principal']['href']))
            for p in post_wp_url_gen:
                post_work_package = self.post_work_package(p, wp_name)
                print("WP: %s P: %s" % ())
                
                            #post_work_package = self.post_work_package(post_wp_url, p, wp_name)
                        #user_id_gen = self.generator(env_wp.get_id_href(user_href_gen))
                # for us in user_id_gen:
                #     print(us)                

        
        
        # _memberships_url = env_wp.base_path + (r['_links']['self']['href'])
        # m_response = env_wp.get_response(_memberships_url)
        # print(_memberships_url)
            # for m in m_response['_embedded']['elements']:
            #     member_href = ['principal']['href']
            #     member = env_wp.get_id_href(member_href)
            #     print(member)
                
            #work_package_url = env_wp.get_project_workpackages_url(_project_id)
            # response = env_wp.post_response(work_package_url, env_wp.get_payload(_project_id, wp_ref, name, description, start_date, due_date))
            # print(response)

    def cron_check_scheduled_tasks(self):
        env_s_tasks = self.env['op.scheduled.tasks']
        tasks = env_s_tasks.get_data(self.limit)
        for t in tasks:
            t_name = t.name
            t_frequency = t.frequency
            t_description = env_s_tasks.verify_field_empty(t.description)
            
            if(t_frequency=="daily"):
                self.post_daily_task(t_name, t_description)
            
    """TODO:
        1. Get project ID
        2. Get project members
        3. Create Task
        4. Add Members to task"""