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
    reason_ids = fields.Many2many(
        "dom.patient.appointment.reason",
        string=_("Reason for visit"),
    )
    present_illness = fields.Text(string=_("Present Illness"))

    # Physical exam fields
    weight = fields.Float(string=_("Weight (kg)"))
    height = fields.Float(string=_("Height (m)"))
    bmi = fields.Float(string="BMI", compute="_compute_bmi", store=True)
    abdominal_circumference = fields.Float(string=_("Abdominal Circumference (cm)"))
    blood_pressure_systolic = fields.Integer(string=_("Blood Pressure (Systolic)"))
    blood_pressure_diastolic = fields.Integer(string=_("Blood Pressure (Diastolic)"))
    heart_rate = fields.Integer(string=_("Heart Rate"))
    respiratory_rate = fields.Integer(string=_("Respiratory Rate"))
    general = fields.Text(string=_("General"))
    cardiopulmonary = fields.Text(string=_("Cardiopulmonary"))
    thyroid = fields.Text(string=_("Thyroid"))
    right_breast = fields.Text(string=_("Right_breast"))
    left_breast = fields.Text(string=_("Left_breast"))
    abdomen = fields.Text(string=_("Abdomen"))
    extremities = fields.Text(string=_("Extremities"))
    neurological = fields.Text(string=_("Neurological"))

    # Background fields
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

    @api.depends("weight", "height")
    def _compute_bmi(self):
        for record in self:
            if record.weight and record.height:
                bmi = record.weight / (record.height**2)
                record.bmi = bmi

    def write(self, vals):
        if self.state == "cancelled":
            raise UserError(_("Can't modify a cancelled appointment"))
        return super().write(vals)
