from odoo import models, fields, api


class SalesOrderStation(models.Model):
    _inherit = 'sale.order'

    is_station_sales = fields.Boolean(default=False)

    parent_dec_id = fields.Many2one('station_operation.station_day_end_close')

class PurchOrderStation(models.Model):
    _inherit = 'purchase.order'

    is_station_purch = fields.Boolean(default=False)

    parent_dec_id = fields.Many2one('station_operation.station_day_end_close')

