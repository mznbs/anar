# -*- coding: utf-8 -*-
# from odoo import http


# class BsSalesIntegration(http.Controller):
#     @http.route('/station_operation/station_operation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/station_operation/station_operation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('station_operation.listing', {
#             'root': '/station_operation/station_operation',
#             'objects': http.request.env['station_operation.station_operation'].search([]),
#         })

#     @http.route('/station_operation/station_operation/objects/<model("station_operation.station_operation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('station_operation.object', {
#             'object': obj
#         })
