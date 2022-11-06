# -*- coding: utf-8 -*-
from odoo import models, fields, api

# import pyodbc



class station_day_end_close_sale_by_gun_line(models.Model):
    _name = 'station_operation.station_day_end_close_sale_by_gun_line'
    _inherit = "station_operation.station_day_end_close_sale_line"

    tank_code = fields.Char(string="Tank Code")
    gun = fields.Char(string="gun")
    opening_reading = fields.Float(default=0.0, help="Opening Reading", string='Opening Reading')
    closing_reading = fields.Float(default=0.0, help="Closing Reading", string='Closing Reading')
    reading_diff = fields.Float(default=0.0, help="Reading Differance", string='Reading Differance',
                                compute='_compute_diff')
    reading_vs_qty = fields.Float(default=0.0, help="Reading vs Quantity", string='Reading vs Quantity',
                                  compute='_compute_reading_vs_qty')

    def _compute_diff(self):
        for row in self:
            row.reading_diff = row.closing_reading - row.opening_reading

    def _compute_reading_vs_qty(self):
        for row in self:
            row.reading_vs_qty = abs(row.reading_diff - row.qty)