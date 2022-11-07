from odoo import models, fields, api


class city(models.Model):
    _name = 'station_operation.city'
    _description = 'City'

    name = fields.Char()

class station(models.Model):
    _name = 'station_operation.station'
    _description = 'Station'

    name = fields.Char()
    description = fields.Text()
    start_date = fields.Date('Date')




