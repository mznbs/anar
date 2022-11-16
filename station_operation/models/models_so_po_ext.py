from odoo import models, fields, api





class station_opertation_template_product(models.Model):
    _inherit = "product.template"

    evap_loss_accepted_sales = fields.Float(string='Accepted Evaporation Loss% Sales ⛽', digits=(16, 4), default=0.002)
    evap_loss_accepted_receivings = fields.Float(string='Accepted Evaporation Loss% Receiving 🚛', digits=(16, 4),
                                                 default=0.002)
    station_operation_icon = fields.Char(string="", default="")




class SalesOrderStation(models.Model):
    _inherit = 'sale.order'

    is_station_sales = fields.Boolean(default=False)

    parent_dec_id = fields.Many2one('station_operation.station_day_end_close')




class SalesOrderStation(models.Model):
    _inherit = 'stock.quant'

    is_station_invent_adjustment = fields.Boolean(default=False)

    parent_dec_id = fields.Many2one('station_operation.station_day_end_close')


class PurchOrderStation(models.Model):
    _inherit = 'purchase.order'

    is_station_purch = fields.Boolean(default=False)

    parent_dec_id = fields.Many2one('station_operation.station_day_end_close')

