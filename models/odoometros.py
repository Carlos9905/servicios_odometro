from odoo import models, api, fields
from odoo.exceptions import ValidationError


class Odometros(models.Model):
    _name = "servicios.odometros"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Servicios Odometros"

    name = fields.Char(
        "Numero de operacion", required=True, default="New", readonly=True
    )
    unidad = fields.Many2one("fleet.vehicle", string="Unidad", required=True)
    costo = fields.Float(string="Costo")
    fecha = fields.Date(string="Fecha")
    tipo_carga = fields.Selection(
        string="Tipo Carga",
        selection=[("servicio", "Servicio"), ("combustible", "Combustible")],
    )
    _tipo_carga = fields.Many2one("fleet.vehicle.log.services", string="Tipo Carga")
    odo_inicial = fields.Float(
        string="Odomtro Inicial", compute="_calculo_odoInicial", store=True
    )
    odo_final = fields.Float(string="Odometro Final")
    litros = fields.Float(string="Litros")
    km_acumulado = fields.Float(string="Kilomtros acumuladsos")
    ren_optimo = fields.Float(string="Rendimiento Optimo")

    @api.model
    def create(self, vals):
        recs = super(Odometros, self).create(vals)

        """Logica"""
        for rec in recs:

            if rec.name == "New":
                rec.name = (
                    self.env["ir.sequence"].next_by_code("secuencia.odometros") or "New"
                )

            if rec.odo_final <= 0:
                raise ValidationError(
                    "El Valor del odometro final no puede ser menor ó igual 0"
                )
            else:
                registros = self.env["km.finales"]
                registros.create(
                    {
                        "tipo": "servicio"
                        if rec._tipo_carga
                        else "combustible",  # "servicio" if record._tipo_carga else "combustible",
                        "odo_final": rec.odo_final,  # record.odo_final,
                        "unidad": rec.unidad.license_plate,  # record.unidad.license_plate,
                        "servicio": rec.name,  # record.name,
                    }
                )
        ##########################
        """ Aquí iria otro codigo para crear un servicio """

        """ #################################### """
        return rec

    @api.depends("odo_final")
    def _calculo_odoInicial(self):
        for record in self:
            registros = self.env["km.finales"].search(
                [("tipo", "=", "servicio" if record._tipo_carga else "combustible")]
            )
            filtro = registros.filtered(
                lambda f: f.odo_final > 0 and f.unidad == record.unidad.license_plate
            )
            lista_km = filtro.mapped("odo_final")
            print(lista_km)
            if len(lista_km) > 1:
                for i in range(len(lista_km)):
                    record.odo_inicial = lista_km[i - 1]
            else:
                record.odo_inicial = record.odo_final

    @api.ondelete(at_uninstall=False)
    def delete_record(self):
        for record in self:
            registros = self.env["km.finales"].search([("servicio", "=", record.name)])
            registros.unlink()

    """
    #@api.model
    def write(self, vals):
        recs = super(Odometros, self).write(vals)
        for rec in recs:
            print(rec.name)
        
        return recs"""

class KmFinales(models.Model):
    _name = "km.finales"

    tipo = fields.Char("Tipo")
    odo_final = fields.Float("Odometro final")
    unidad = fields.Char("Unidad")
    servicio = fields.Char("Servicio al que pertenece")
