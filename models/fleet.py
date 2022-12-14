from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class Fleet(models.Model):
    _inherit = "fleet.vehicle.log.services"

    ser_id = fields.Many2one("servicios.odometros", "Servicio y Odometro")
    litros = fields.Float("Litros")

    amount = fields.Monetary("Cost")
    date = fields.Datetime(
        help="Date when the cost has been executed", default=datetime.now()
    )

    def _get_odometer(self):
        self.odometer = 0
        for record in self:
            if record.odometer_id or record.ser_id:
                record.odometer = record.odometer_id.value
                record.odometer = record.ser_id.odo_final
                record.amount = record.ser_id.costo
                record.date = record.ser_id.fecha
                record.purchaser_id = record.ser_id.operador
                record.litros = record.ser_id.litros

    def _set_odometer(self):
        print("Se ejecuto")
        for record in self:
            if not record.odometer:
                raise UserError(
                    _("Emptying the odometer value of a vehicle is not allowed.")
                )
            odometer = self.env["fleet.vehicle.odometer"].create(
                {
                    "value": record.odometer,
                    "date": record.date or fields.Date.context_today(record),
                    "vehicle_id": record.vehicle_id.id,
                }
            )
            servi = self.env["servicios.odometros"].create(
                {
                    "odo_final": record.odometer,
                    "costo": record.amount,
                    "fecha": record.date or fields.Date.context_today(record),
                    "tipo_carga": record.service_type_id.id,
                    "unidad": record.vehicle_id.id,
                    "litros": record.litros,
                    "operador": record.purchaser_id.id
                }
            )
            self.odometer_id = odometer
            self.ser_id = servi
