# -*- coding: utf-8 -*-
# from odoo import http


# class Openproject(http.Controller):
#     @http.route('/openproject/openproject/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/openproject/openproject/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('openproject.listing', {
#             'root': '/openproject/openproject',
#             'objects': http.request.env['openproject.openproject'].search([]),
#         })

#     @http.route('/openproject/openproject/objects/<model("openproject.openproject"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('openproject.object', {
#             'object': obj
#         })
