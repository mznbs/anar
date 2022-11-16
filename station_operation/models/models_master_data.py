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
    # city_id = color = fields.manytoone('City')
    station_code = fields.Char()
    address = fields.Char("Address")

    name = fields.Char()
    description = fields.Text()
    start_date = fields.Date('Start Date')
    latest_closing_date = fields.Date('Latest Date')

    tank_ids = fields.One2many('station_operation.tank',
                               'station_id')
    gun_ids = fields.One2many('station_operation.gun',
                              'station_id')
    location_id = fields.Many2one('stock.location')


    product_icons = fields.Char("Products",compute='_calc_product_icons')

    @api.depends("tank_ids", "gun_ids")
    def _calc_product_icons(self):
        for rec in self:
            rec.product_icons = ""
            list_of_icons =[]
            if rec.tank_ids:
                for tank in rec.tank_ids:
                    list_of_icons.append(tank.product_id.station_operation_icon)
                rec.product_icons += ''.join(set(list_of_icons))


class tank(models.Model):
    _name = 'station_operation.tank'
    _description = 'Tank'
    _rec_name = 'common_name'

    common_name = fields.Char('Tank Name', compute='_calc_name', compute_sudo=True)

    @api.depends("tank_code", "product_id", "station_id")
    def _calc_name(self):
        for rec in self:
            rec.common_name = " - "
            if rec.product_id.name:
                rec.common_name = rec.product_id.name
            if rec.tank_code:
                rec.common_name = rec.common_name + " - " + str(rec.tank_code)
            if rec.station_id.name:
                rec.common_name = rec.common_name + " - " + rec.station_id.name

    # id = color = fields.Integer('ID')
    tank_code = color = fields.Integer('Tank Code')
    description = fields.Text()
    start_date = fields.Date('Date')
    station_id = fields.Many2one('station_operation.station')
    product_id = fields.Many2one('product.product')

    oil_code = color = fields.Integer('Oil Code')
    grade_specific_id = color = fields.Integer('GradeSpecificID')

    gun_ids = fields.One2many('station_operation.gun',
                              'tank_id')
    product_icon = fields.Char(compute='_calc_product_icon', string='')

    @api.depends("product_id")
    def _calc_product_icon(self):
        for rec in self:
            rec.product_icon = rec.product_id.station_operation_icon


class gun(models.Model):
    _name = 'station_operation.gun'
    _description = 'Gun1'
    _rec_name = 'common_name'

    common_name = fields.Char('Gun Name', compute='_calc_name', compute_sudo=True)

    @api.depends("tank_code", "product_id", "station_id")
    def _calc_name(self):
        for rec in self:
            rec.common_name = rec.product_id.name
            if rec.gun_code:
                rec.common_name = str(rec.gun_code) + " - " + rec.product_id.name
            if rec.station_id.name:
                rec.common_name = rec.common_name + " - " + rec.station_id.name

    # id = color = fields.Integer('Gun Code')
    gun_code = fields.Char("Gun Code")
    tank_code = fields.Char("Tank Code")
    port_code = fields.Char("Port Code")

    description = fields.Text()
    station_id = fields.Many2one('station_operation.station')
    tank_id = fields.Many2one('station_operation.tank')
    product_id = fields.Many2one('product.product')
    product_icon = fields.Char(compute='_calc_product_icon', string='')

    @api.depends("product_id")
    def _calc_product_icon(self):
        for rec in self:
            rec.product_icon = rec.product_id.station_operation_icon
