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
        required=True,
        domain=[("is_patient", "=", True)],
    )
    appointment_id = fields.Many2one(
        "dom.patient.appointment",
        string=_("Appointment"),
        ondelete="cascade",
        readonly=True,
    )
    state = fields.Selection(related="appointment_id.state")
