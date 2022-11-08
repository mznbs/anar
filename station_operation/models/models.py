# -*- coding: utf-8 -*-
from odoo import models, fields, api

import pymssql

sql_update_hose_reading_diff = """
UPDATE OilTransactions
SET          difference = [View_calcHoseReadingDiff].diff
FROM     [View_calcHoseReadingDiff] INNER JOIN
                  OilTransactions ON [View_calcHoseReadingDiff].id = OilTransactions.ID
WHERE  (OilTransactions.difference = - 1) OR
                  (OilTransactions.difference IS NULL)
"""
#
# cnxnlocal_old = pyodbc.connect(
#     'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-H7EA1N4;DATABASE=center5;Trusted_Connection=yes;')

# live  37.224.107.7     dbanaradmin     anar#123456$admin
# cnxn = pyodbc.connect(    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=37.224.107.7;DATABASE=Center;UID=dbanaradmin;PWD=anar#123456$admin;')

cnxn = pymssql.connect(server='37.224.107.7', user='dbanaradmin', password='anar#123456$admin',
                       database='Center')




def _get_stations(self):
    sql_get_station = "select Name from dbo.Stations"
    cursor = cnxn.cursor()
    cursor.execute(sql_get_station)
    rows = cursor.fetchall()
    list = []
    for row in rows:
        list.append((row[0], row[0]))  # Name
    return list


# linking with the main product table
class station_opertation_template_product(models.Model):
    _inherit = "product.template"

    evap_loss_accepted_sales = fields.Float(string='Accepted Evaporation Loss% ⛽', digits=(16, 4), default=0.002)
    evap_loss_accepted_receivings = fields.Float(string='Accepted Evaporation Loss% ⛽', digits=(16, 4), default=0.002)
    station_operation_icon = fields.Char(string="Product Icon", default="")


class station_day_end_close(models.Model):
    _name = 'station_operation.station_day_end_close'
    _description = 'Station Day End Closing Header'

    name = fields.Char()
    description = fields.Text()
    station = fields.Selection(_get_stations, string='Station', required=True)
    date_of_closing = fields.Date('Date', required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    invoice_user_id = fields.Many2one(
        string='person',
        comodel_name='res.users',
        copy=False,
        tracking=True,
        default=lambda self: self.env.user,
    )

    station_day_end_close_tank_line_ids = fields.One2many('station_operation.station_day_end_close_tank_line',
                                                          'parent_id')
    sales_order_ids = fields.One2many('sale.order',
                                      'parent_dec_id')
    purch_order_ids = fields.One2many('purchase.order',
                                      'parent_dec_id')

    station_day_end_close_lines_sale_ids = fields.One2many('station_operation.station_day_end_close_sale_line',
                                                           'parent_id')
    station_day_end_close_lines_sale_by_gun_ids = fields.One2many(
        'station_operation.station_day_end_close_sale_by_gun_line',
        'parent_id')

    # @api.onchange('date_of_closing')
    # def onchange_date_of_closing(self):
    #     self.name=str(self.date_of_closing)+"🟢🔴"
    #     # for row in self.station_day_end_close_lines_sale_ids:
    #     #     row.qty=row.qty+1
    #     #     #row.search([('1', '=', '1')])
    #     #self.calc_sales_qty()
    #     self.calc_all_sales()

    def test_sql3(self):
        sql = """
            INSERT INTO [dbo].[temp]           ([name])
                 VALUES           ('test')
            """
        cursor = cnxn.cursor()
        cursor.execute(sql)
        cnxn.commit()
        cnxn.close()

    def run_sql_pymssql(self, sql):
        cnxn = pymssql.connect(server='37.224.107.7', user='dbanaradmin', password='anar#123456$admin',
                               database='Center')
        cursor = cnxn.cursor()
        cursor.execute(sql)
        cnxn.commit()
        cnxn.close()

    def calc_all_sales(self):
        self.calc_sales_qty_by_gun()
        self.calc_sales_qty()

    def calc_sales_qty_by_gun(self):
        # clear lines
        self.station_day_end_close_lines_sale_by_gun_ids.unlink()

        sql_get_sales_sum_by_gun = """
            SELECT 
            OilTransactions.StationID, --0
            OilTransactions.TType,      --1
             SUM(OilTransactions.AMN) AS valueSr,--2
             OilTransactions.PPU AS unitPrice, --3
             SUM(OilTransactions.Volume) AS Volume,--4
              TransactionTypes.TransactionTypeDesc_en,--5
               GradeSpecifics.Name,  --6 
                      GradeSpecifics.Code, --7
                       OilTransactions.GunId, --8
                       dbo.fn_get_hose_opening(MAX(OilTransactions.ID)) AS opening_reading, --9
                       dbo.fn_get_hose_closing(MAX(OilTransactions.ID)) AS closing_reading, --10
                       GunConfig_station.TANKCODE --11
    FROM     OilTransactions INNER JOIN
                      TransactionTypes ON TransactionTypes.TransactionTypeID = OilTransactions.TType INNER JOIN
                      GradeSpecifics ON GradeSpecifics.GradeSpecificID = OilTransactions.GradeSpecificID INNER JOIN
                      GunConfig_station ON OilTransactions.GunId = GunConfig_station.GUNCODE
    WHERE  (CAST(OilTransactions.TrueTime AS date) = '%s/%s/%s') AND (NOT (OilTransactions.Volume = 0))
    GROUP BY OilTransactions.StationID, OilTransactions.TType, TransactionTypes.TransactionTypeDesc_en, GradeSpecifics.Name, OilTransactions.PPU, GradeSpecifics.Code, OilTransactions.GunId, GunConfig_station.TANKCODE
    """

        cursor = cnxn.cursor()
        sql = sql_get_sales_sum_by_gun % (
            str(self.date_of_closing.month), str(self.date_of_closing.day)
            , str(self.date_of_closing.year)
        )
        cursor.execute(sql)
        rows = cursor.fetchall()
        print("read : " + str(len(rows)))

        for row in rows:
            # create lines
            vals = {
                'product_id': self.env['product.product'].search([('name', '=', row[6])])[0].id,  # row.Name
                'parent_id': self.id,
                'type': row[5],  # .TransactionTypeDesc_en
                'gun': row[8],  # GunId
                'qty': row[4],  # Volume
                'unit_price': row[3],  # unitPrice
                'opening_reading': row[9],  # opening_reading
                'closing_reading': row[10],  # closing_reading
                'tank_code': row[11],  # TANKCODE
                'line_amount': row[4] * row[3]  # row.Volume * row.unitPrice
            }
            self.env['station_operation.station_day_end_close_sale_by_gun_line'].create(vals)
            print("done : ")

    def calc_sales_qty(self):
        sql_get_sales_sum = """SELECT  
         OilTransactions.StationID,--0
          OilTransactions.TType, --1
          SUM(OilTransactions.AMN) AS valueSr,--2
           OilTransactions.PPU AS unitPrice,--3
            SUM(OilTransactions.Volume) AS Volume,--4
             TransactionTypes.TransactionTypeDesc_en, --5
                              GradeSpecifics.Name,--6
                               GradeSpecifics.Code--7
            FROM     OilTransactions INNER JOIN
                              TransactionTypes ON TransactionTypes.TransactionTypeID = OilTransactions.TType INNER JOIN
                              GradeSpecifics ON GradeSpecifics.GradeSpecificID = OilTransactions.GradeSpecificID
            WHERE  (      (CAST(OilTransactions.TrueTime AS date) = '""" + str(
            self.date_of_closing.month) + """/""" + str(self.date_of_closing.day) + """/""" + str(
            self.date_of_closing.year) + """') AND (NOT (OilTransactions.Volume = 0)))
            GROUP BY OilTransactions.StationID, OilTransactions.TType, TransactionTypes.TransactionTypeDesc_en, GradeSpecifics.Name, OilTransactions.PPU, GradeSpecifics.Code
            """

        cursor = cnxn.cursor()
        cursor.execute(sql_get_sales_sum)
        rows = cursor.fetchall()

        print("read : " + str(len(rows)))

        # clear lines
        self.station_day_end_close_lines_sale_ids.unlink()

        for row in rows:
            # create lines
            vals = {
                'product_id': self.env['product.product'].search([('name', '=', row[6])])[0].id,  # Name
                'parent_id': self.id,
                'type': row[5],  # TransactionTypeDesc_en
                'qty': row[4],  # Volume
                'unit_price': row[3],  # unitPrice
                'line_amount': row[4] * row[3]  # row.Volume * row.unitPrice
            }
            self.env['station_operation.station_day_end_close_sale_line'].create(vals)
            print("done : ")

    def create_sales(self):
        # product91 = self.env['product.product'].search([('name', '=', '91')])[0]
        # product95 = self.env['product.product'].search([('name', '=', '95')])[0]
        # # price_list = self.env['product.pricelist'].search([('name', '=', "jed mak")])[0]
        order_lines = []

        for sl in self.station_day_end_close_lines_sale_ids:
            order_lines.append((0, 0, {
                'product_id': sl.product_id.id,  # product95.id,
                # 'name': sl.product_id,  # product95.name,
                'product_uom_qty': sl.qty,  # self.qty95cash,
                # 'price_unit': 2.30,
                'create_date': self.date_of_closing,
            }))

        vals = {
            'name': 'virtual station customer',
            'state': "draft",
            'partner_id': 2,
            'date_order': self.date_of_closing,
            # 'pricelist_id': price_list.id,
            # 'create_date': self.date_of_closing,
            'commitment_date': self.date_of_closing,
            'order_line': order_lines,
            'parent_dec_id': self.id
        }
        self.env['sale.order'].create(vals)

    def sendMail(self):
        public_users = self.env.ref('station_operation.station_operation_manager').users

        for user in public_users:
            # if user.user_has_groups('station_operation.station_operation_manager'):
            if user.email_normalized:
                self.send_mail_to_user(user)
        # return {
        #     'warning': {'title': "Warning", 'message': "What is this?", 'type': 'notification'},
        # }

    def send_mail_to_user(self, user):
        template = self.env.ref('station_operation.station_dec_stander')
        assert template._name == 'mail.template'

        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        # for user in self:
        # if not user.email:
        #     raise UserError(_("Cannot send email: user %s has no email address.", user.name))
        email_values['email_to'] = user.email_normalized  # "eng.tarek83@gmail.com"  # user.email
        # TDE FIXME: make this template technical (qweb)
        # with self.env.cr.savepoint():

        # context = self._context
        # current_uid = context.get('uid')
        # user = self.env['res.users'].browse(current_uid)

        # user.id
        template.send_mail(self.id, force_send=True, raise_exception=True, email_values=email_values)

    # _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    def create_purch(self):
        vend_Aramco = self.env['res.partner'].search([('name', 'ilike', 'aramco')])[0]

        order_lines = []

        for tank_line in self.station_day_end_close_tank_line_ids:
            for tank_line_detail_receiving in tank_line.line_detail_ids:
                if tank_line_detail_receiving.totalIn > 0:
                    order_lines.append((0, 0, {
                        'product_id': tank_line.product_id.id,  # product95.id,
                        'product_uom_qty': tank_line_detail_receiving.totalIn,
                        'product_qty': tank_line_detail_receiving.totalIn,
                        'create_date': self.date_of_closing,
                    }))

        vals = {
            'name': vend_Aramco.name,
            'partner_id': vend_Aramco.id,
            'state': "draft",
            'date_order': self.date_of_closing,
            'order_line': order_lines,
            'parent_dec_id': self.id,
        }
        self.env['purchase.order'].create(vals)

        # if self.res_model and self.res_id:
        #     return self.env[self.res_model].browse(self.res_id).get_formview_action()
        # return False

    def prepare_tanks(self):
        self.run_sql_pymssql(sql_update_tank_diff)

        # clear lines
        self.station_day_end_close_tank_line_ids.unlink()

        day = str(self.date_of_closing.day)
        mth = str(self.date_of_closing.month)
        year = str(self.date_of_closing.year)

        cursor_tanks = cnxn.cursor()

        sql_get_tank_measures2 = """
        SELECT TankCode,--0
         item,--1
          StationID,--2
          [dbo].[fn_get_tank_opening](TankCode , %s ,%s,%s ) as opening_qty,--3
          [dbo].[fn_get_tank_closing](TankCode , %s,%s,%s ) as closing_qty--4
        FROM     View_Tank_master
        where StationName='%s'
        """
        sql_statment = sql_get_tank_measures2 % (day, mth, year, day, mth, year, self.station)
        cursor_tanks.execute(sql_statment)
        tanks = cursor_tanks.fetchall()
        for tank in tanks:
            if tank[3]:  # opening_qty
                tank_guns_total_sales = 0.0
                for gn in filter(lambda x: x.tank_code == str(tank[0]),  # TankCode
                                 self.station_day_end_close_lines_sale_by_gun_ids):
                    tank_guns_total_sales = tank_guns_total_sales + gn.qty

                vals = {
                    'tank': tank[0],  # TankCode
                    'opening_qty': tank[3],  # opening_qty
                    'closing_qty': tank[4],  # closing_qty
                    # 'qty_in':  calculated,
                    'parent_id': self.id,
                    'tank_guns_total_sales': tank_guns_total_sales,
                    'product_id': self.env['product.product'].search([('name', '=', tank[1])])[0].id,  # item
                }
                res_inserted_tank_lines = self.env['station_operation.station_day_end_close_tank_line'].create(vals)

                # tank details to get one receiving
                cursor_receiving = cnxn.cursor()

                # as openingQty, --0
                # as closingQty, --1
                # as totalIn, --2
                # as startTime, --3
                # as endTime - -4

                sql_statment_receiving = sql_tank_reciving % (
                    tank[0], day, mth, year)  # TankCode # % (day, mth, year, day, mth, year, self.station)
                cursor_receiving.execute(sql_statment_receiving)
                tanks_receiving = cursor_receiving.fetchall()
                for tank_receive in tanks_receiving:
                    vals_receiving = {
                        'parent_tank_line_id': res_inserted_tank_lines.id,
                        'openingQty': tank_receive[0],  # openingQty
                        'closingQty': tank_receive[1],  # closingQty
                        'totalIn': tank_receive[2],  # totalIn
                        'startTime': tank_receive[3],  # startTime
                        'endTime': tank_receive[4],  # endTime
                    }
                    self.env['station_operation.station.dec.tank.line.details'].create(vals_receiving)

                rec_qty_evaporation = res_inserted_tank_lines.opening_qty + res_inserted_tank_lines.qty_in - res_inserted_tank_lines.tank_guns_total_sales - res_inserted_tank_lines.closing_qty
                res_inserted_tank_lines.write({'qty_evaporation': rec_qty_evaporation})


class station_day_end_close_sale_line(models.Model):
    _name = 'station_operation.station_day_end_close_sale_line'
    _description = 'Station Day End Closing Sale Lines'

    name = fields.Char(string="Name")
    parent_id = fields.Many2one('station_operation.station_day_end_close')
    product_id = fields.Many2one('product.product')
    product_icon = fields.Char(compute='_calc_product_icon', string='')

    @api.depends("product_id")
    def _calc_product_icon(self):
        for rec in self:
            rec.product_icon = rec.product_id.station_operation_icon

    # gun = fields.Char(string="Tank")
    qty = fields.Float(default=0.0, help="Quantity", string='Quantity')
    unit_price = fields.Float(default=0.0, string='Unit Price')
    line_amount = fields.Float(default=0.0, string='line amount')
    type = fields.Char(string="Type")

    forman_qty = fields.Float(default=0.0, help="Forman Quantity", string='Forman Quantity')
    forman_diff_qty = fields.Float(default=0.0, help="Difference", string='Difference Quantity',
                                   compute='_compute_diff')

    def _compute_diff(self):
        for row in self:
            row.forman_diff_qty = row.forman_qty + 888

            # tanks
            # pumps readings


class station_day_end_close_tank_line(models.Model):
    _name = 'station_operation.station_day_end_close_tank_line'
    _description = 'Station Day End Closing Lines'

    name = fields.Char(string="Name")
    parent_id = fields.Many2one('station_operation.station_day_end_close')
    tank = fields.Char(string="Tank")
    opening_qty = fields.Float(default=0.0, string='Opening Qty')
    closing_qty = fields.Float(default=0.0, string='Closing Qty')
    tank_guns_total_sales = fields.Float(default=0.0, string='Tank Sales Qty')
    qty_in = fields.Float(default=0.0, help="qty_in", compute='_calc_reciving', string='qty Receiving')

    qty_evaporation = fields.Float(default=0.0, string='Evaporation')
    # qty_evaporation_calculated = fields.Float(default=0.0, compute='_calc_evaporation', string='Evaporation Calculated')
    qty_evaporation_allowed = fields.Float(default=0.0, compute='_calc_evaporation_allowed',
                                           string='Evaporation Allowed')

    line_detail_ids = fields.One2many('station_operation.station.dec.tank.line.details',
                                      'parent_tank_line_id')

    product_id = fields.Many2one('product.product')
    product_icon = fields.Char(compute='_calc_product_icon', string='')

    @api.depends("product_id")
    def _calc_product_icon(self):
        for rec in self:
            rec.product_icon = rec.product_id.station_operation_icon
    @api.depends("line_detail_ids")
    def _calc_reciving(self):
        for rec in self:
            tot = 0.0
            for line in rec.line_detail_ids:
                tot += line.totalIn
            rec.qty_in = tot



    # @api.depends("line_detail_ids", "opening_qty", "qty_in", "tank_guns_total_sales", "closing_qty")
    # def _calc_evaporation(self):
    #     for rec in self:
    #             rec.qty_evaporation_calculated = rec.opening_qty + rec.qty_in - rec.tank_guns_total_sales - rec.closing_qty

    @api.depends("product_id", "opening_qty", "qty_in", "tank_guns_total_sales", "closing_qty")
    def _calc_evaporation_allowed(self):
        for rec in self:
            rec.qty_evaporation_allowed = \
                rec.product_id.evap_loss_accepted_sales * rec.tank_guns_total_sales + \
                rec.product_id.evap_loss_accepted_receivings * rec.qty_in
            # self.env['product.product'].search([('name', '=', rec.product_id)])[0].id,


class station_dec_tank_line_details(models.Model):
    _name = 'station_operation.station.dec.tank.line.details'
    _description = 'Station Day End Closing Line Details'
    _rec_name = 'common_name'

    common_name = fields.Char('common_name', compute='_calc_name', compute_sudo=True)
    openingQty = fields.Float(default=0.0, string='Opening Qty')
    closingQty = fields.Float(default=0.0, string='Closing Qty')
    totalIn = fields.Float(default=0.0, help="qty_in", string='qty in')
    startTime = fields.Datetime('Start Receiving', default=lambda self: fields.Datetime.now())
    endTime = fields.Datetime('End Receiving', default=lambda self: fields.Datetime.now())

    parent_tank_line_id = fields.Many2one('station_operation.station_day_end_close_tank_line')

    @api.depends("totalIn")
    def _calc_name(self):
        for rec in self:
            rec.common_name = str(rec.totalIn)


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


sql_tank_reciving = """
declare @date_time_start_in as datetime
declare @date_time_stop_in  as datetime
declare @TankID as  bigint
declare @day as int ,@month  as int , @year as int
set @TankID=%s
set @day=%s
set @month=%s
set @year=%s

SELECT  @date_time_start_in = [dbo].[fn_get_tank_start_receiving_time](@TankID  ,@day  ,@month  ,@year)
SELECT  @date_time_stop_in = [dbo].[fn_get_tank_end_receiving_time](@TankID  ,@day  ,@month  ,@year)

declare @opening_before_receiving as  float
declare @closing_after_receiving as  float
declare @total_in as  float
--todo take the reading before it
SELECT @opening_before_receiving =  OilVol  FROM     TankStatus_log_Station WHERE  (ID = @TankID) AND (Time < @date_time_start_in)	  order by Time

  --adding five minutes after 
SELECT top 1 @closing_after_receiving = OilVol  FROM     TankStatus_log_Station WHERE  (ID = @TankID) AND (Time < DATEADD(mi, 5,   @date_time_stop_in)) 	  order by Time  desc

----without adding five minutes after 
--SELECT @closing_after_receiving = OilVol  FROM     TankStatus_log_Station WHERE  (ID = @TankID) AND (Time = @date_time_stop_in) 	  order by Time
-- SELECT  @closing_after_receiving

 set @total_in =  @closing_after_receiving - @opening_before_receiving

select  @opening_before_receiving as openingQty  ,--0
  @closing_after_receiving as closingQty,--1
    @total_in as totalIn ,--2
       @date_time_start_in as startTime ,--3
        @date_time_stop_in  as endTime --4

"""

sql_update_tank_diff = """  UPDATE TankStatus_log_Station
SET    difference = View_calcTankDiff.diff
FROM     View_calcTankDiff INNER JOIN
   TankStatus_log_Station ON View_calcTankDiff.recId = TankStatus_log_Station.recId
WHERE  (TankStatus_log_Station.difference = - 1) OR
   (TankStatus_log_Station.difference IS NULL)
"""
