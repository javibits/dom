from datetime import datetime
from odoo import _, api, fields, models


class Patient(models.Model):
    _inherit = "res.partner"
    _order = "sequence asc"
    _sql_constraints = [
        (
            "dom_patient_id_unique",
            "UNIQUE (id_number)",
            _("Identification number must be unique."),
        ),
        (
            "dom_patient_sequence_unique",
            "UNIQUE (sequence)",
            _("Patient # must be unique."),
        ),
    ]

    is_patient = fields.Boolean(
        string=_("Is a Patient?"),
        default=False,
    )
    sequence = fields.Char(
        string=_("Patient #"),
        readonly=True,
    )
    id_number = fields.Char(string=_("ID Number"))
    dob = fields.Date(string=_("Birthdate"))
    age = fields.Integer(string=_("Age"), compute="_compute_age", store=True)
    birthplace = fields.Char(string=_("Birthplace"))
    gender = fields.Selection(
        [
            ("male", _("Male")),
            ("female", _("Female")),
        ],
        string=_("Gender"),
    )
    marital_status = fields.Selection(
        [
            ("single", _("Single")),
            ("married", _("Married")),
            ("common_law", _("Common Law")),
            ("separated", _("Separated")),
            ("divorced", _("Divorced")),
            ("widowed", _("Widowed")),
        ],
        string=_("Marital Status"),
        tracking=True,
    )
    profession = fields.Char(string=_("Profession"))
    occupation = fields.Char(string=_("Occupation"))
    blood_type = fields.Selection(
        [
            ("A+", "A+"),
            ("A", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
            ("O+", "O+"),
            ("O-", "O-"),
        ],
        string=_("Blood Type"),
    )
    background_ids = fields.One2many(
        "dom.patient.background",
        "patient_id",
        string=_("Patient Background"),
    )
    personal_background_ids = fields.One2many(
        "dom.patient.background",
        "patient_id",
        compute="_compute_personal_background_ids",
        inverse="_inverse_personal_background_ids",
    )
    family_background_ids = fields.One2many(
        "dom.patient.background",
        "patient_id",
        compute="_compute_family_background_ids",
        inverse="_inverse_family_background_ids",
    )
    psychobiological_habits_background_ids = fields.One2many(
        "dom.patient.background",
        "patient_id",
        compute="_compute_psychobiological_habits_background_ids",
        inverse="_inverse_psychobiological_habits_background_ids",
    )
    sexual_activity_background_ids = fields.One2many(
        "dom.patient.background",
        "patient_id",
        compute="_compute_sexual_activity_background_ids",
        inverse="_inverse_sexual_activity_background_ids",
    )
    other_background_ids = fields.One2many(
        "dom.patient.background",
        "patient_id",
        compute="_compute_other_background_ids",
        inverse="_inverse_other_background_ids",
    )

    appointment_ids = fields.One2many("dom.patient.appointment", "patient_id")
    appointment_count = fields.Integer(
        string=_("Appointment Count"),
        compute="_compute_appointment_count",
    )
    prescription_ids = fields.One2many("dom.patient.prescription", "patient_id")
    prescription_count = fields.Integer(
        string=_("Prescription Count"),
        compute="_compute_prescription_count",
    )
    laboratory_test_order_ids = fields.One2many(
        "dom.laboratory.test.order", "patient_id"
    )
    laboratory_test_order_count = fields.Integer(
        string=_("Laboratory Test Count"),
        compute="_compute_laboratory_test_order_count",
    )
    medical_test_order_ids = fields.One2many("dom.medical.test.order", "patient_id")
    medical_test_order_count = fields.Integer(
        string=_("Medical Test Count"),
        compute="_compute_medical_test_order_count",
    )

    @api.depends("dob")
    def _compute_age(self):
        for patient in self:
            dob = patient.dob
            if dob:
                today = fields.Date.today()
                age = (
                    today.year
                    - dob.year
                    - ((today.month, today.day) < (dob.month, dob.day))
                )
                patient.age = age

    @api.depends("background_ids")
    def _compute_personal_background_ids(self):
        self._compute_background_ids("personal")

    @api.depends("background_ids")
    def _inverse_personal_background_ids(self):
        self._inverse_background_ids("personal")

    @api.depends("background_ids")
    def _compute_family_background_ids(self):
        self._compute_background_ids("family")

    @api.depends("background_ids")
    def _inverse_family_background_ids(self):
        self._inverse_background_ids("family")

    @api.depends("background_ids")
    def _compute_psychobiological_habits_background_ids(self):
        self._compute_background_ids("psychobiological_habits")

    @api.depends("background_ids")
    def _inverse_psychobiological_habits_background_ids(self):
        self._inverse_background_ids("psychobiological_habits")

    @api.depends("background_ids")
    def _compute_sexual_activity_background_ids(self):
        self._compute_background_ids("sexual_activity")

    @api.depends("background_ids")
    def _inverse_sexual_activity_background_ids(self):
        self._inverse_background_ids("sexual_activity")

    @api.depends("background_ids")
    def _compute_other_background_ids(self):
        self._compute_background_ids("other")

    @api.depends("background_ids")
    def _inverse_other_background_ids(self):
        self._inverse_background_ids("other")

    def _compute_background_ids(self, background_type):
        """
        Generic funcition for computing background_ids based on background type

        Args:
            background_type (str): One of the options defined in 'type' selection field
            of 'dom.patient.background' model
        """
        for record in self:
            background = record.background_ids.filtered(
                lambda r: r.type == background_type
            )
            setattr(record, f"{background_type}_background_ids", background)

    def _inverse_background_ids(self, background_type):
        for record in self:
            new_records = getattr(record, f"{background_type}_background_ids").filtered(
                lambda r: not r.id
            )
            deleted_records = record.background_ids.filtered(
                lambda r: r.type == background_type
            ) - getattr(record, f"{background_type}_background_ids")

            record.background_ids -= deleted_records
            record.background_ids |= new_records

    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = self.env["dom.patient.appointment"].search_count(
                [("patient_id", "=", self.id)]
            )

    def _compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env[
                "dom.patient.prescription"
            ].search_count([("patient_id", "=", self.id)])

    def _compute_laboratory_test_order_count(self):
        for record in self:
            record.laboratory_test_order_count = self.env[
                "dom.laboratory.test.order"
            ].search_count([("patient_id", "=", self.id)])

    def _compute_medical_test_order_count(self):
        for record in self:
            record.medical_test_order_count = self.env[
                "dom.medical.test.order"
            ].search_count([("patient_id", "=", self.id)])

    def action_open_appointments(self):
        return {
            "name": "Appointments",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id, "default_date": datetime.now()},
            "type": "ir.actions.act_window",
            "res_model": "dom.patient.appointment",
            "view_mode": "tree,form,calendar",
        }

    def action_open_prescriptions(self):
        return {
            "name": "Prescriptions",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id},
            "type": "ir.actions.act_window",
            "res_model": "dom.patient.prescription",
            "view_mode": "tree,form",
        }

    def action_open_laboratory_test_orders(self):
        return {
            "name": "Laboratory Tests",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id},
            "type": "ir.actions.act_window",
            "res_model": "dom.laboratory.test.order",
            "view_mode": "tree,form",
        }

    def action_open_medical_test_orders(self):
        return {
            "name": "Medical Tests",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id},
            "type": "ir.actions.act_window",
            "res_model": "dom.medical.test.order",
            "view_mode": "tree,form",
        }

    def name_get(self):
        res = []
        for record in self:
            if record.is_patient:
                res.append((record.id, f"{record.sequence} - {record.name}"))
            else:
                res.append((record.id, f"{record.name}"))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("is_patient"):
                vals["sequence"] = self.env["ir.sequence"].next_by_code(
                    "dom.patient.sequence"
                )
        result = super(Patient, self).create(vals_list)
        return result
