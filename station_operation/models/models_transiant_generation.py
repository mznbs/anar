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

            dateExists = self.env['namaa.dates'].sudo().search([
                ('date_value', '=', single_date.date()),
                ('AmPm', '=', "AM"),
            ], limit=1)

            if (len(dateExists) > 0):
                continue

            vals_Details_namaa_driver_dates = []

            if self.state == "all_stations":
                employees = self.env['hr.employee'].search([
                    # ('company_id', '=', self.env.company.id)
                    ('isDriver', '=', 'True')
                    # ('id', 'in', self.employee_ids.ids)
                    #  , ('name', 'ilike', 'هري')
                ])
            elif self.state == "select_drivers":
                employees = self.env['hr.employee'].search([
                    # ('company_id', '=', self.env.company.id)
                    ('id', 'in', self.employee_ids.ids)
                ])

            for employee in employees:
                vals_Details_namaa_driver_dates.append((0, 0, {
                    'date': single_date,
                    'is_confirmed': False,
                    'hr_employee_id': employee.id
                }))

            vals = {
                'nameOfWeekDay': WEEKDAYS[single_date.weekday()],
                'AmPm': 'AM',
                'date_value': single_date,

                # 'namaa_driver_date_ids': vals_Details_namaa_driver_dates,
                'employee_ids': [x[2]['hr_employee_id'] for x in vals_Details_namaa_driver_dates],
            }

            self.env['namaa.dates'].create(vals)
            vals['AmPm'] = "PM"
            self.env['namaa.dates'].create(vals)

    def reload(self):
        return False

