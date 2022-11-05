from odoo import models, fields, api




sql_get_tank_measures2 = """
SELECT TankCode, item, StationID
,[dbo].[fn_get_tank_opening](TankCode , %s ,%s,%s ) as opening_qty
,[dbo].[fn_get_tank_closing](TankCode , %s,%s,%s ) as closing_qty
FROM     View_Tank_master
where StationName='%s'
"""

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

select  @opening_before_receiving as openingQty  ,  @closing_after_receiving as closingQty,  @total_in as totalIn ,   @date_time_start_in as startTime , @date_time_stop_in  as endTime 

"""








sql_update_tank_diff = """  UPDATE TankStatus_log_Station
SET    difference = View_calcTankDiff.diff
FROM     View_calcTankDiff INNER JOIN
   TankStatus_log_Station ON View_calcTankDiff.recId = TankStatus_log_Station.recId
WHERE  (TankStatus_log_Station.difference = - 1) OR
   (TankStatus_log_Station.difference IS NULL)
"""

