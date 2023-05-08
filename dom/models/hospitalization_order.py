from odoo import _, fields, models


class HospitalizationOrder(models.Model):
    _name = "dom.hospitalization.order"
    _inherit = ["dom.order.abstract"]
    _description = "Hospitalization Order"
    _order = "date desc, patient_id asc"

    place = fields.Char(string=_("Place"), required=True)
    diagnosis = fields.Text(string=_("Diagnosis"), required=True)
    recomendations = fields.Text(string=_("Recomendations"), required=True)

    def name_get(self):
        res = []
        for record in self:
            res.append(
                (
                    record.id,
                    f"{record.date}: {record.patient_id.name} - {record.place}",
                )
            )
        return res
