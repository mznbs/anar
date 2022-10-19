# -*- coding: utf-8 -*-

from odoo import models, fields, api


class bs_sales_integration(models.Model):
    _name = 'bs_sales_integration.bs_sales_integration'
    _description = 'bs_sales_integration.bs_sales_integration'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
