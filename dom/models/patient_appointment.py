from odoo import _, fields, models
from odoo.exceptions import UserError


class PatientAppointment(models.Model):
    _name = "dom.patient.appointment"
    _description = "Patient Appointment"
    _order = "date desc"
    rec_name = "patient_id"

    _sql_constraints = [
        (
            "dom_patient_appointment_date_unique",
            "UNIQUE (patient_id, date)",
            _("Patient already has an appointment on this date."),
        ),
    ]

    active = fields.Boolean(string=_("Active"), default=True)
    patient_id = fields.Many2one(
        "res.partner",
        string=_("Patient"),
        ondelete="cascade",
        required=True,
        domain=[("is_patient", "=", True)],
    )
    date = fields.Date(string=_("Date"), required=True)
    state = fields.Selection(
        [
            ("draft", _("Pending")),
            ("in_progress", _("In progress")),
            ("done", _("Done")),
            ("cancelled", _("Cancelled")),
        ],
        string="State",
        readonly=True,
        default="draft",
    )

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, f"{record.patient_id.name}"))
        return res

    def button_in_progress(self):
        self.state = "in_progress"

    def button_done(self):
        self.state = "done"

    def button_cancel(self):
        self.state = "cancelled"

    def write(self, vals):
        if self.state == "cancelled":
            raise UserError(_("Can't modify a cancelled appointment"))
        return super().write(vals)
