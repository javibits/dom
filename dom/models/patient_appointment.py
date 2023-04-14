from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PatientAppointment(models.Model):
    _name = "dom.patient.appointment"
    _description = "Patient Appointment"
    _order = "date desc"

    _sql_constraints = [
        (
            "dom_patient_appointment_date_unique",
            "UNIQUE (patient_id, date)",
            _("Patient already has an appointment on this date."),
        ),
    ]

    active = fields.Boolean(string=_("Active"), default=True)
    name = fields.Char(string=_("Name"), compute="_compute_name")
    number = fields.Integer(
        string=_("Appointment #"),
        compute="_compute_appointment_number",
    )
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
    diagnosis_ids = fields.Many2many(
        "dom.patient.diagnosis",
        string=_("Diagnostic Impression"),
    )
    evolution = fields.Text(string=_("Evolution"))

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
    right_breast = fields.Text(string=_("Right breast"))
    left_breast = fields.Text(string=_("Left breast"))
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

    def _compute_name(self):
        for appointment in self:
            appointment.name = f"({appointment.number}) - {appointment.patient_id.name}"

    def _compute_appointment_number(self):
        for record in self:
            patient_appointments = self.search(
                [("patient_id", "=", record.patient_id.id)],
                order="date asc",
            )
            for index, appointment in enumerate(patient_appointments, start=1):
                appointment.number = index

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
