from odoo import models, api, fields
from odoo.exceptions import ValidationError


class Odometros(models.Model):
    _name = "servicios.odometros"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Servicios Odometros"

    name = fields.Integer("Numero de operacion", required=True)
    unidad = fields.Many2one("fleet.vehicle", string="Unidad")
    costo = fields.Float(string="Costo")
    fecha = fields.Date(string="Fecha")
    tipo_carga = fields.Selection(
        string="Tipo de carga",
        selection=[("combustible", "Combustible"), ("servicio", "Servicio")],
        default="combustible",
    )
    odo_inicial = fields.Float(
        string="Odomtro Inicial", compute="_calculo_odoInicial", store=True
    )
    odo_final = fields.Float(string="Odometro Final")
    litros = fields.Float(string="Litros")
    km_acumulado = fields.Float(string="Kilomtros acumuladsos")
    ren_optimo = fields.Float(string="Rendimiento Optimo")

    """
    km_finales = fields.One2many(
        "km.finales",
        "servicio_id",
        string="Kilometros registrados",
    )
    """
    @api.constrains("odo_final")
    def check(self):
        for record in self:
            if record.odo_final <= 0:
                ValueError("El Valor del odometro final no puede ser menor ó igual 0")

    @api.onchange("odo_final")
    def _registrar(self):
        for record in self:
            registros = self.env["km.finales"]
            registros.create({
                "tipo":record.tipo_carga,
                "odo_final":record.odo_final
            })
    @api.depends("odo_final")
    def _calculo_odoInicial(self):
        for record in self:
            registros = self.env["km.finales"].search([('tipo', '=', record.tipo_carga)])          
            lista_km = registros.mapped(lambda f: f.odo_final > 0)

            if len(lista_km) > 1:
                for i in range(len(lista_km)):
                    record.odo_inicial = lista_km[i - 1]
            else:
                record.odo_inicial = record.odo_final


class KmFinales(models.Model):
    _name = "km.finales"

    tipo = fields.Char("Tipo")
    odo_final = fields.Float("Odometro final")
    servicio_id = fields.Many2one(
        "servicios.odometros", string="Servicio al que pertence"
    )
