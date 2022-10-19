# -*- coding: utf-8 -*-
# from odoo import http


# class BsSalesIntegration(http.Controller):
#     @http.route('/bs_sales_integration/bs_sales_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bs_sales_integration/bs_sales_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('bs_sales_integration.listing', {
#             'root': '/bs_sales_integration/bs_sales_integration',
#             'objects': http.request.env['bs_sales_integration.bs_sales_integration'].search([]),
#         })

#     @http.route('/bs_sales_integration/bs_sales_integration/objects/<model("bs_sales_integration.bs_sales_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bs_sales_integration.object', {
#             'object': obj
#         })
