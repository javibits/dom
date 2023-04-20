from datetime import datetime
from odoo import _, api, Command, fields, models
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
    patient_active = fields.Boolean(related="patient_id.active")
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
    neck = fields.Text(string=_("Neck"))
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
    prescription_id = fields.Many2one(
        "dom.patient.prescription",
        string=_("Prescription"),
        ondelete="set null",
    )
    prescription_line_ids = fields.One2many(
        related="prescription_id.line_ids",
        readonly=False,
    )
    pharmacological_treatment_ids = fields.Many2many(
        "dom.pharmacological.treatment",
        string=_("Pharmacological Treatments"),
    )
    laboratory_test_order_id = fields.Many2one(
        "dom.laboratory.test.order",
        string=_("Laboratory Test Order"),
        ondelete="set null",
    )
    laboratory_test_order_line_ids = fields.One2many(
        related="laboratory_test_order_id.line_ids",
        readonly=False,
    )
    laboratory_test_profile_ids = fields.Many2many(
        "dom.laboratory.test.profile",
        string=_("Laboratory Test Profiles"),
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

    def button_create_prescription(self):
        prescription = self.env["dom.patient.prescription"].create(
            {
                "patient_id": self.patient_id.id,
                "appointment_id": self.id,
            }
        )
        self.prescription_id = prescription

    def button_create_laboratory_test_order(self):
        laboratory_test_order = self.env["dom.laboratory.test.order"].create(
            {
                "patient_id": self.patient_id.id,
                "appointment_id": self.id,
            }
        )
        self.laboratory_test_order_id = laboratory_test_order

    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for appointment in self:
            if appointment.start_time and appointment.end_time:
                duration = appointment.end_time - appointment.start_time
                appointment.duration = duration.total_seconds() / 3600.0
            else:
                appointment.duration = 0.0

    @api.onchange("pharmacological_treatment_ids")
    def _onchange_pharmacological_treatment_ids(self):
        """
        Updates prescription_line_ids based on pharmacological treatments selected.
        Each time a treatment is selected, the prescription_line_ids is recreated
        """
        medicines = []
        self.prescription_line_ids = [Command.clear()]
        for treatment in self.pharmacological_treatment_ids:
            for medicine in treatment.medicine_ids:
                medicines.append(
                    Command.create({"medicine_id": medicine.id}),
                )
        self.prescription_line_ids = medicines

    @api.onchange("laboratory_test_profile_ids")
    def _onchange_laboratory_test_profile_ids(self):
        """
        Updates laboratory_test_order_line_ids based on laboratory test profiles selected.
        Each time a profile is selected, the laboratory_test_order_line_ids is recreated
        """
        laboratory_tests = []
        self.laboratory_test_order_line_ids = [Command.clear()]
        for profile in self.laboratory_test_profile_ids:
            for laboratory_test in profile.laboratory_test_ids:
                laboratory_tests.append(
                    Command.create({"laboratory_test_id": laboratory_test.id}),
                )
        self.laboratory_test_order_line_ids = laboratory_tests

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
