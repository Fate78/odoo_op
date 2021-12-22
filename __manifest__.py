# -*- coding: utf-8 -*-
{
    'name': "openproject",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version' : '0.1',
    'license' : 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/op.project_view.xml',
        'views/templates.xml',
        'views/op.user_view.xml',
        'views/op.activity_view.xml',
        'views/op.workpackage_view.xml',
        'views/op.time_entries_view.xml',
        'views/project_activity_view.xml',
        'views/res_config_settings_inherited_view.xml',
        'views/op.versions_view.xml',
        'wizard/views/sync_projects_view.xml',
        'wizard/views/sync_workpackages_view.xml',
        'wizard/views/sync_versions_view.xml',
        'wizard/views/sync_time_entries_view.xml',
        #'wizard/views/post_projects_view.xml',
        #'wizard/views/update_projects_view.xml',
        #'wizard/views/post_work_packages_view.xml',
        #'wizard/views/update_work_packages_view.xml',
        #'wizard/views/post_time_entries_view.xml',
        'wizard/views/update_time_entries_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
