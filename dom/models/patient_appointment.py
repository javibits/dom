from datetime import datetime
from odoo import _, api, fields, models
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
    start_time = fields.Datetime(string=_("Start Time"))
    end_time = fields.Datetime(string=_("End Time"))
    duration = fields.Float(
        string=_("Duration"),
        compute="_compute_duration",
        store=True,
    )
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
    personal_background_ids = fields.One2many(
        related="patient_id.personal_background_ids",
        readonly=False,
    )
    family_background_ids = fields.One2many(
        related="patient_id.family_background_ids",
        readonly=False,
    )
    psychobiological_habits_background_ids = fields.One2many(
        related="patient_id.psychobiological_habits_background_ids",
        readonly=False,
    )
    sexual_activity_background_ids = fields.One2many(
        related="patient_id.sexual_activity_background_ids",
        readonly=False,
    )
    other_background_ids = fields.One2many(
        related="patient_id.other_background_ids",
        readonly=False,
    )

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, f"{record.patient_id.name}"))
        return res

    def button_in_progress(self):
        self.state = "in_progress"
        if not self.start_time:
            self.start_time = datetime.now()

    def button_done(self):
        self.state = "done"
        if not self.end_time:
            self.end_time = datetime.now()

    def button_cancel(self):
        self.state = "cancelled"

    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for appointment in self:
            if appointment.start_time and appointment.end_time:
                duration = appointment.end_time - appointment.start_time
                appointment.duration = duration.total_seconds() / 3600.0
            else:
                appointment.duration = 0.0

    def write(self, vals):
        if self.state == "cancelled":
            raise UserError(_("Can't modify a cancelled appointment"))
        return super().write(vals)
