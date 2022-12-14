from odoo import fields, api, models

class LogService(models.Model):
    _inherit = "fleet.vehicle.odometer"

    conductor = fields.Many2one("hr.employee", string="Conductor")
    odometro_inicial = fields.Float("Odometro Inicial")
    num_operacion = fields.Char("Numero de operacion")
    costo = fields.Float("Costo")
    litros = fields.Float("Litros")
    km_acumulado = fields.Float("Kilometros acumulados", compute = "_cal_km_acumulado")
    red_optimo = fields.Float("Rendiemineto Optimo", compute = "_cal_ren_optimo")

    @api.depends("odometro_inicial", "value")
    def _cal_km_acumulado(self):
        suma = 0
        for record in self:
            suma = record.value - record.odometro_inicial
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

    @api.model
    def create(self, vals):
        print("Ejecucion")
        res = super(LogService, self).create(vals)
        for record in res:
            registros = self.env["fleet.vehicle.odometer"].search(
                [("vehicle_id", "=", record.vehicle_id.id)]
            )
            lista_km = registros.mapped("value")
            print(lista_km)
            print(record.value)
            if len(lista_km) > 1:
                for i in range(len(lista_km)):
                    record.odometro_inicial = lista_km[i - 1]
            else:
                record.odometro_inicial = record.value
        return res