from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class Fleet(models.Model):
    _inherit = "fleet.vehicle.log.services"

    num_operacion = fields.Char("Número de operación", readonly=True, default="Nuevo")
    litros = fields.Float("Litros")
    odometro_inicial = fields.Float("Odometro Inicial")
    conductor = fields.Many2one("hr.employee", string="Conductor")
    red_optimo = fields.Float("Rendimiento optimo")
    km_acumulado = fields.Float("Kilometros acumulados",  compute="_get_km_acumulado", store=True)
    enable_km_anterior = fields.Boolean("Habilitar", default=False)

    @api.model
    def create(self, vals):
        if vals.get("num_operacion", ("Nuevo")) == ("Nuevo"):
            vals["num_operacion"] = self.env["ir.sequence"].next_by_code(
                "secuencia.odometros"
            ) or ("New")
        return super(Fleet, self).create(vals)

    @api.depends("odometer", "odometro_inicial")
    def _get_km_acumulado(self):
        suma = 0
        for record in self:
            suma = record.odometer - record.odometro_inicial
            record.km_acumulado = suma if suma > 0 else suma * -1

    def _get_odometer(self):
        self.odometer = 0
        for record in self:
            if record.odometer_id:
                record.odometer = record.odometer_id.value
                record.odometro_inicial = record.odometer_id.odometro_inicial
                record.conductor = record.odometer_id.conductor

    def _set_odometer(self):
        for record in self:
            if not record.odometer:
                raise UserError(
                    _("Emptying the odometer value of a vehicle is not allowed.")
                )
            odometer = self.env["fleet.vehicle.odometer"].create(
                {
                    "num_operacion":record.num_operacion,
                    "value": record.odometer,
                    "date": record.date or fields.Date.context_today(record),
                    "vehicle_id": record.vehicle_id.id,
                    "odometro_inicial": record.odometro_inicial,
                    "conductor": record.conductor.id
                }
            )
            self.odometer_id = odometer

    @api.ondelete(at_uninstall=False)
    def delete_record(self):
        for record in self:
            registros = self.env["fleet.vehicle.odometer"].search(
                [("num_operacion", "=", record.num_operacion)]
            )
            registros.unlink()

    @api.onchange("vehicle_id", "odometer")
    def _get_km_anterior(self):
        registros = self.env["fleet.vehicle.odometer"].search([("vehicle_id", "=", self.vehicle_id.id)])
        lista_km = registros.mapped("value")
        if len(lista_km) > 0:
            self.odometro_inicial = lista_km[len(lista_km) - 1]
        else:
            self.odometro_inicial = self.odometer
    @api.onchange("odometer")
    def _check_km(self):
        if self.odometer < self.odometro_inicial:           
            res = {'warning': {
            'title': _('Warning'),
            'message': _('El Odometro Actual es menor que el Odometro Anterior, ¿Deseas Continuar con la operación?')
            }}
            if res:
                return res
    
    #Alerta de costo elevado
    @api.onchange("amount")
    def _check_costo(self):
        if self.amount > 25.0:#Este valor se puede cambiar
            res = {'warning': {
            'title': _('Warning'),
            'message': _('El costo esta fuera del precio')
            }}
            if res:
                return res