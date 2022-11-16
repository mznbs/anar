# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api





WEEKDAYS = ['الاثنين', 'الثلاثاء', 'الاربعاء', 'الخميس', 'الجمعة', 'السبت', 'الاحد']



class station_generate_dates(models.TransientModel):
    _name = "station.generate.dates"
    _description = "Generate Dates"

    @api.model
    def _default_language(self):
        return False

    weekday_include_mon = fields.Boolean(WEEKDAYS[0], default=True)
    weekday_include_tue = fields.Boolean(WEEKDAYS[1], default=True)
    weekday_include_wed = fields.Boolean(WEEKDAYS[2], default=True)
    weekday_include_thu = fields.Boolean(WEEKDAYS[3], default=True)
    weekday_include_fri = fields.Boolean(WEEKDAYS[4], default=False)
    weekday_include_sat = fields.Boolean(WEEKDAYS[5], default=False)
    weekday_include_sun = fields.Boolean(WEEKDAYS[6], default=True)


    start_date = fields.Datetime('From', default=fields.Datetime.now)
    end_date = fields.Datetime('To', default=fields.Datetime.now() + timedelta(days=3))
    station_ids = fields.Many2many('station_operation.station', 'station_generate_dates_rel', 'station_generate_dates_id',
                                    'station_id',
                                    string='Stations')

    state = fields.Selection([('all_stations', 'all_stations'), ('select_stations', 'select_stations')],
                             string='Stations', default='all_stations')



    def generate(self):

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)

        for single_date in daterange(self.start_date, self.end_date):

            # filter weekdays
            if single_date.weekday() == 0 and self.weekday_include_mon == 0: continue
            if single_date.weekday() == 1 and self.weekday_include_tue == 0: continue
            if single_date.weekday() == 2 and self.weekday_include_wed == 0: continue
            if single_date.weekday() == 3 and self.weekday_include_thu == 0: continue
            if single_date.weekday() == 4 and self.weekday_include_fri == 0: continue
            if single_date.weekday() == 5 and self.weekday_include_sat == 0: continue
            if single_date.weekday() == 6 and self.weekday_include_sun == 0: continue

            dateExists = self.env['station_operation.station_day_end_close'].sudo().search([
                ('date_of_closing', '=', single_date.date()),
                #('AmPm', '=', "AM"),
            ], limit=1)

            if (len(dateExists) > 0):
                continue

            vals_Details_station_dates = []

            if self.state == "all_stations":
                stations = self.env['hr.employee'].search([
                     ('company_id', '=', self.env.company.id)
                  #  ,('active', '=', 'True')
                ])
            elif self.state == "select_stations":
                stations = self.env['station_operation.station'].search([
                    # ('company_id', '=', self.env.company.id)
                    ('id', 'in', self.station_ids.ids)
                ])

            # for station_ in stations:
            #     vals_Details_station_dates.append((0, 0, {
            #         'date': single_date,
            #         'is_confirmed': False,
            #         'hr_employee_id': station_.id
            #     }))

            vals = {
                #'nameOfWeekDay': WEEKDAYS[single_date.weekday()],
                'date_of_closing': single_date,
                #'employee_ids': [x[2]['hr_employee_id'] for x in vals_Details_station_dates],
            }

            self.env['station_operation.station_day_end_close'].create(vals)
            # vals['AmPm'] = "PM"
            # self.env['station_operation.station_day_end_close'].create(vals)

    def reload(self):
        return False

