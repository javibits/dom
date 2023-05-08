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
    patient_gender = fields.Selection(related="patient_id.gender")
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
        ondelete="restrict",
    )
    present_illness = fields.Text(string=_("Present Illness"))
    diagnosis_ids = fields.Many2many(
        "dom.patient.diagnosis",
        string=_("Diagnostic Impression"),
        ondelete="restrict",
    )
    evolution = fields.Text(string=_("Evolution and Management Plan"))

    # Physical exam fields
    weight = fields.Float(string=_("Weight (kg)"))
    height = fields.Float(string=_("Height (m)"))
    bmi = fields.Float(string="BMI", compute="_compute_bmi", store=True)
    abdominal_circumference = fields.Float(string=_("Abdominal Circumference (cm)"))
    blood_pressure_systolic = fields.Integer(string=_("Blood Pressure (Systolic)"))
    blood_pressure_diastolic = fields.Integer(string=_("Blood Pressure (Diastolic)"))
    heart_rate = fields.Integer(string=_("Heart Rate"))
    respiratory_rate = fields.Integer(string=_("Respiratory Rate"))
    temperature = fields.Float(string=_("Temperature"))
    general = fields.Text(string=_("General"))
    cardiopulmonary = fields.Text(string=_("Cardiopulmonary"))
    neck = fields.Text(string=_("Neck"))
    right_breast = fields.Text(string=_("Right breast"))
    left_breast = fields.Text(string=_("Left breast"))
    abdomen = fields.Text(string=_("Abdomen"))
    rectal = fields.Text(string=_("Rectal Palpation"))
    extremities = fields.Text(string=_("Extremities"))
    neurological = fields.Text(string=_("Neurological"))

    # Gynecological examination fields
    external_genitalia = fields.Text(string=_("External Genitalia"))
    cervicovaginal = fields.Text(string=_("Cervicovaginal"))
    vaginal_palpation = fields.Text(string=_("Vaginal Palpation"))
    colposcopy = fields.Text(string=_("Colposcopy"))
    cytology = fields.Text(string=_("Cytology"))

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
    prescription_order_id = fields.Many2one(
        "dom.prescription.order",
        string=_("Prescription"),
        ondelete="set null",
    )
    prescription_order_line_ids = fields.One2many(
        related="prescription_order_id.line_ids",
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
        string=_("Laboratory Test Order Lines"),
        readonly=False,
    )
    laboratory_test_profile_ids = fields.Many2many(
        "dom.laboratory.test.profile",
        string=_("Laboratory Test Profiles"),
    )
    medical_test_order_id = fields.Many2one(
        "dom.medical.test.order",
        string=_("Medical Test Order"),
        ondelete="set null",
    )
    medical_test_clinical_summary = fields.Text(
        related="medical_test_order_id.clinical_summary",
        readonly=False,
    )
    medical_test_order_line_ids = fields.One2many(
        related="medical_test_order_id.line_ids",
        string=_("Medical Test Order Lines"),
        readonly=False,
    )
    medical_test_profile_ids = fields.Many2many(
        "dom.medical.test.profile",
        string=_("Medical Test Profiles"),
    )
    referral_order_ids = fields.One2many(
        "dom.referral.order",
        "appointment_id",
        string=_("Referral Orders"),
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
        prescription = self.env["dom.prescription.order"].create(
            {
                "patient_id": self.patient_id.id,
                "appointment_id": self.id,
            }
        )
        self.prescription_order_id = prescription

    def button_create_laboratory_test_order(self):
        laboratory_test_order = self.env["dom.laboratory.test.order"].create(
            {
                "patient_id": self.patient_id.id,
                "appointment_id": self.id,
            }
        )
        self.laboratory_test_order_id = laboratory_test_order

    def button_create_medical_test_order(self):
        medical_test_order = self.env["dom.medical.test.order"].create(
            {
                "patient_id": self.patient_id.id,
                "appointment_id": self.id,
            }
        )
        self.medical_test_order_id = medical_test_order

    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for appointment in self:
            if appointment.start_time and appointment.end_time:
                duration = appointment.end_time - appointment.start_time
                appointment.duration = duration.total_seconds() / 3600.0
            else:
                appointment.duration = 0.0

    ############################################################################
    # _onchange_pharmacological_treatment_ids, _onchange_laboratory_test_profile_ids and
    # _onchange_medical_test_profile_ids could be simplified with a parameterized function
    # but is left explicit for more clarity

    @api.onchange("pharmacological_treatment_ids")
    def _onchange_pharmacological_treatment_ids(self):
        """
        Updates prescription_order_line_ids based on pharmacological treatments selected.
        Each time a treatment is selected, the prescription_order_line_ids is recreated
        """
        medicines = []
        self.prescription_order_line_ids = [Command.clear()]
        for treatment in self.pharmacological_treatment_ids:
            for medicine in treatment.medicine_ids:
                medicines.append(
                    Command.create({"medicine_id": medicine.id}),
                )
        self.prescription_order_line_ids = medicines

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

    @api.onchange("medical_test_profile_ids")
    def _onchange_medical_test_profile_ids(self):
        """
        Updates medical_test_order_line_ids based on medical test profiles selected.
        Each time a profile is selected, the medical_test_order_line_ids is recreated
        """
        medical_tests = []
        self.medical_test_order_line_ids = [Command.clear()]
        for profile in self.medical_test_profile_ids:
            for medical_test in profile.medical_test_ids:
                medical_tests.append(
                    Command.create({"medical_test_id": medical_test.id}),
                )
        self.medical_test_order_line_ids = medical_tests

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

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        """
        Hide 'gynecological examination' fields depending on config parameter
        """
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            active_gynecological_evaluation = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("dom.gynecological_evaluation")
            )

            if not active_gynecological_evaluation:
                notebook_page_node = arch.xpath(
                    "//page[@name='gynecological_examination']"
                )
                if notebook_page_node:
                    notebook_page_node = notebook_page_node[0]
                    notebook_page_node.set("invisible", "1")
        return arch, view
