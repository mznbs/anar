from odoo import models, fields, api


class city(models.Model):
    _name = 'station_operation.city'
    _description = 'City'

    name = fields.Char()

class station(models.Model):
    _name = 'station_operation.station'
    _description = 'Station'


    id = color = fields.Integer('Station ID')
    bs_id = fields.Integer('BlueSky Station ID')
    #city_id = color = fields.manytoone('City')
    station_code = fields.Char()
    address = fields.Char("Address")

    name = fields.Char()
    description = fields.Text()
    start_date = fields.Date('Start Date')
    latest_closing_date = fields.Date('Latest Date')

    tank_ids=fields.One2many('station_operation.tank',
                                      'station_id')
    gun_ids=fields.One2many('station_operation.gun',
                                      'station_id')

class tank(models.Model):
    _name = 'station_operation.tank'
    _description = 'Tank'

    id = color = fields.Integer('Tank Code')
    name = fields.Char()
    description = fields.Text()
    start_date = fields.Date('Date')
    station_id = fields.Many2one('station_operation.station')
    product_id = fields.Many2one('product.product')
    gun_ids=fields.One2many('station_operation.gun',
                                      'tank_id')
    product_icon = fields.Char(compute='_calc_product_icon', string='')

    @api.depends("product_id")
    def _calc_product_icon(self):
        for rec in self:
            rec.product_icon = rec.product_id.station_operation_icon

class gun(models.Model):
    _name = 'station_operation.gun'
    _description = 'Gun'

    id = color = fields.Integer('Gun Code')
    name = fields.Char()
    description = fields.Text()
    station_id = fields.Many2one('station_operation.station')
    tank_id = fields.Many2one('station_operation.tank')
    product_id = fields.Many2one('product.product')
    product_icon = fields.Char(compute='_calc_product_icon', string='')

    @api.depends("product_id")
    def _calc_product_icon(self):
        for rec in self:
            rec.product_icon = rec.product_id.station_operation_icon


