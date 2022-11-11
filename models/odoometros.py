from odoo import models, api, fields


class Odometros(models.Model):
    _name = "servicios.odometros"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Servicios Odometros"

    name = fields.Integer('Numero de operacion', required=True)
    unidad = fields.Many2one('fleet.vehicle', string='Unidad')
    costo = fields.Float(string='Costo')
    fecha = fields.Date(string='Fecha')
    tipo_carga = fields.Selection(
        string="Tipo de carga",
        selection=[("combustible", "Combustible"), ("servicio", "Servicio")],
    )
    odo_inicial = fields.Float(string='Odomtro Inicial')
    odo_final = fields.Float(string='Odometro Final')
    litros = fields.Float(string='Litros')
    km_acumulado = fields.Float(string='Kilomtros acumuladsos')
    ren_optimo = fields.Float(string='Rendimiento Optimo')
