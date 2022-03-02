from asyncore import write
from pdb import post_mortem
from time import time
from requests.models import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import *
import hashlib
import json
import logging

_logger = logging.getLogger(__name__)


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

        hashable = str(project_id) + name + responsible_id
        hashed = hashlib.md5(hashable.encode("utf-8")).hexdigest()
        print("Inside Hash: ", hashable)
        return hashed

    def post_work_package(self, project_id, responsible_id, main_url, name, description, start_date):
        env = self.env['op.work.package']
        response = env.post_response(main_url, env.get_payload(project_id, responsible_id, name, description,start_date))

    def get_memberships_href(self,p_url):
        env_wp = self.env['op.work.package']
        response_project = env_wp.get_response(p_url)
        memberships_href = response_project['_links']['memberships']['href']

        return memberships_href

    def post_scheduled_task(self, name, description, project_id):
        hashed_op = hashlib.sha256()
        hashed_new = hashlib.sha256()
        env_wp = self.env['op.work.package']
        wp_page_url = env_wp.get_workpackages_url()
        response_work_package = env_wp.get_response(wp_page_url)
        now = datetime.now().strftime("%Y-%m-%d")

        start_date = now
        wp_name = name + "_" + now
        is_admin=None
        admin_id=None
        task_exists=None

        next_offset_wp = True
        next_offset_memb = True

        project_url = env_wp.get_project_url(project_id)
        memberships_href = self.get_memberships_href(project_url)
        response_members = env_wp.get_response(env_wp.base_path + memberships_href)
        project_wp_url = env_wp.get_project_workpackages_url(project_id)

        try:
            if(response_members['count']!=0):
                while next_offset_memb:
                    for i in response_members['_embedded']['elements']:
                        user_id = env_wp.get_id_href(i['_links']['principal']['href'])
                        for r in i['_links']['roles']:
                            role_id = env_wp.get_id_href(r['href'])
                            if(role_id=="3"):
                                is_admin=True
                                admin_id=user_id
                        #Verify if task has already been created in case the cron is running more than once 
                            while next_offset_wp:
                                for rw in response_work_package['_embedded']['elements']:
                                    _name = rw['subject']
                                    _id_project = env_wp.get_id_href(rw['_links']['project']['href'])
                                    _responsible = env_wp.verify_field_empty(rw['_links']['responsible']['href'])
                                    _responsible = env_wp.get_id_href(_responsible)
                                    hashed_op = self.get_hashed(_id_project, _name, _responsible)
                                    hashed_new = self.get_hashed(project_id, wp_name, admin_id)
                                    if(hashed_op==hashed_new):
                                        task_exists=True
                                    else:
                                        task_exists=False
                                next_offset_wp, response_work_package = env_wp.check_next_offset(next_offset_wp, response_work_package)
                            
                        next_offset_memb, response_members = env_wp.check_next_offset(next_offset_memb, response_members)
            if(task_exists==False and is_admin==True):
                post_work_package = env_wp.post_response(project_wp_url, env_wp.get_payload(project_id, admin_id, wp_name, description, start_date))
                print("Posting WP: ", project_id, admin_id, wp_name, description, start_date) 
        except Exception as e:
            _logger.error('Error: %s' % e)

    def cron_check_scheduled_tasks(self):
        env_s_tasks = self.env['op.scheduled.tasks']
        tasks = env_s_tasks.get_data(self.limit)
        now=datetime.now()

        for t in tasks:
            t_name = t.name
            t_frequency = t.frequency
            t_project = t.projects.db_id
            t_description = env_s_tasks.verify_field_empty(t.description)
            t_interval = t.interval
            t_run_today = t.run_today
            t_active = t.active
            t_write_date = t.write_date
            t_write_date_test = t.write_date_test

            vals = {
                    'run_today':False,
                    'write_date':now,
                    'write_date_test':now
                    }

            if(t_active == True):
                #Check next run date->compare to now
                if(t_frequency=="daily"):
                    next_run_date = t_write_date_test + relativedelta(days=+t_interval)
                    print("----Daily Task----")
                    print("Now: ", now)
                    print("Next Run: ", next_run_date)
                    print("Last Run: ", t_write_date_test)
                    if(now>=next_run_date or t_run_today==True):
                        try:
                            print("Going for a run")
                            self.post_scheduled_task(t_name, t_description, t_project)
                            tasks.write(vals)
                        except Exception as e:
                            _logger.error('Error: %s' % e)

                elif(t_frequency=="weekly"):
                    next_run_date = t_write_date_test + relativedelta(weeks=+t_interval)
                    print("----Weekly Task----")
                    print("Now: ", now)
                    print("Next Run: ", next_run_date)
                    print("Last Run: ", t_write_date_test)
                    if(now>=next_run_date or t_run_today==True):
                        try:
                            print("Going for a run")
                            self.post_scheduled_task(t_name, t_description, t_project)
                            tasks.write(vals)
                        except Exception as e:
                            _logger.error('Error: %s' % e)

                elif(t_frequency=="monthly"):
                    next_run_date = t_write_date_test + relativedelta(months=+t_interval)
                    print("----Monthly Task----")
                    print("Now: ", now)
                    print("Next Run: ", next_run_date)
                    print("Last Run: ", t_write_date_test)
                    if(now>=next_run_date or t_run_today==True):
                        try:
                            print("Going for a run")
                            self.post_scheduled_task(t_name, t_description, t_project)
                            tasks.write(vals)
                        except Exception as e:
                            _logger.error('Error: %s' % e)