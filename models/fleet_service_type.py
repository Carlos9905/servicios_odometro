from odoo import models, fields, api


class FleetServiceType(models.Model):
    _inherit = "fleet.service.type"

    category = fields.Selection(
        string="Categoria",
        selection=[("contract", "Contrato"), ("service", "Servicio"), ("combustible","Combustible")],
    )
