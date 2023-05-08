from odoo import _, api, models, fields


class DOMOrderAbstract(models.AbstractModel):
    _name = "dom.order.abstract"
    _description = "DOM Order Abstract"

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

    @api.depends("appointment_id")
    def _compute_patient_id_onchange(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
        else:
            self.patient_id = None
