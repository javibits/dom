from odoo import _, api, fields, models


class HospitalizationOrder(models.Model):
    _name = "dom.hospitalization.order"
    _description = "Hospitalization Order"
    _order = "date desc, patient_id asc"

    date = fields.Date(
        string=_("Date"),
        default=fields.Date.context_today,
        readonly=True,
    )
    patient_id = fields.Many2one(
        "res.partner",
        string=_("Patient"),
        ondelete="cascade",
        compute="_compute_patient_id_onchange",
        store=True,
        readonly=False,
        required=True,
        domain=[("is_patient", "=", True)],
    )
    appointment_id = fields.Many2one(
        "dom.patient.appointment",
        string=_("Appointment"),
        ondelete="cascade",
    )
    place = fields.Char(string=_("Place"), required=True)
    diagnosis = fields.Text(string=_("Diagnosis"), required=True)
    recomendations = fields.Text(string=_("Recomendations"), required=True)

    @api.depends("appointment_id")
    def _compute_patient_id_onchange(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
        else:
            self.patient_id = None

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
