from odoo import models, api, fields
from odoo.exceptions import ValidationError


class Odometros(models.Model):
    _name = "servicios.odometros"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Servicios Odometros"

    name = fields.Char(
        "Numero de operacion", required=True, default="New", readonly=True
    )
    unidad = fields.Many2one(
        "fleet.vehicle", string="Unidad", required=True, readonly=True
    )
    costo = fields.Float(string="Costo")
    fecha = fields.Datetime(string="Fecha")
    tipo_carga = fields.Many2one(
        "fleet.service.type", string="Tipo Carga", readonly=True
    )
    odo_inicial = fields.Float(
        string="Odomtro Inicial", compute="_calculo_odoInicial", store=True
    )
    odo_final = fields.Float(string="Odometro Final")
    litros = fields.Float(string="Litros")
    operador = fields.Many2one("res.partner", string="Operador")

    km_acumulado = fields.Float(
        string="Kilomtros acumuladsos", compute="_cal_km_acumulado", store=True
    )
    ren_optimo = fields.Float(
        string="Rendimiento Optimo", compute="_cal_ren_optimo", store=True
    )

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
                        if rec.tipo_carga.category != "combustible"
                        else "combustible",
                        "odo_final": rec.odo_final,
                        "unidad": rec.unidad.license_plate,  # Aqui va el numero de unidad
                        "servicio": rec.name,  # record.name,
                    }
                )
        return rec

    @api.depends("odo_final")
    def _calculo_odoInicial(self):
        for record in self:
            registros = self.env["km.finales"].search(
                [
                    (
                        "tipo",
                        "=",
                        "servicio"
                        if record.tipo_carga.category != "combustible" #Este era el error
                        else "combustible",
                    )
                ]
            )
            filtro = registros.filtered(
                lambda f: f.odo_final > 0
                and f.unidad
                == record.unidad.license_plate  # Aqui va el numero de unidad
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

    def write(self, vals):
        # Vals devuelve un diccionario con solo los datos de los campos editados
        print(vals)

        registros = self.env["km.finales"].search([("servicio", "=", self.name)])
        tipo_c = registros.mapped("tipo")
        print(tipo_c)
        registros.write(
            {
                "odo_final": vals["odo_final"]
                if "odo_final" in vals
                else self.odo_final,  # vals["odo_final"],
                "servicio": vals["servicio"] if "servicio" in vals else self.name,
            }
        )
        return super(Odometros, self).write(vals)

    @api.depends("odo_final", "odo_inicial")
    def _cal_km_acumulado(self):
        suma = 0
        for record in self:
            suma = record.odo_final - record.odo_inicial
        self.km_acumulado = suma if suma > 0 else suma * -1

    @api.depends("litros", "km_acumulado")
    def _cal_ren_optimo(self):
        suma = 0
        for record in self:
            if record.litros > 0:
                suma = record.km_acumulado / record.litros
            else:
                suma = 0
        self.ren_optimo = suma


class KmFinales(models.Model):
    _name = "km.finales"

    tipo = fields.Char("Tipo")
    odo_final = fields.Float("Odometro final")
    unidad = fields.Char("Unidad")
    servicio = fields.Char("Servicio al que pertenece")
