from odoo import _, api, fields, models


class Patient(models.Model):
    _inherit = "res.partner"
    _sql_constraints = [
        (
            "dom_patient_id_unique",
            "UNIQUE (id_number)",
            _("Identification number must be unique."),
        ),
    ]

    id_number = fields.Char(string=_("ID Number"), required=True)
    dob = fields.Date(string=_("Birthdate"), required=True)
    age = fields.Integer(string=_("Age"), compute="_compute_age", store=True)
    birthplace = fields.Char(string=_("Birthplace"))
    gender = fields.Selection(
        [
            ("male", _("Male")),
            ("female", _("Female")),
        ],
        string=_("Gender"),
        required=True,
    )

    marital_status = fields.Selection(
        [
            ("single", _("Single")),
            ("married", _("Married")),
            ("divorced", _("Divorced")),
            ("widowed", _("Widowed")),
        ],
        string=_("Marital Status"),
        tracking=True,
    )
    profession = fields.Char(string=_("Profession"))
    occupation = fields.Char(string=_("Occupation"))
    history_ids = fields.One2many(
        "dom.patient.history",
        "patient_id",
        string=_("Patient History"),
    )
    personal_history_ids = fields.One2many(
        "dom.patient.history",
        "patient_id",
        compute="_compute_personal_history_ids",
        inverse="_inverse_personal_history_ids",
    )
    family_history_ids = fields.One2many(
        "dom.patient.history",
        "patient_id",
        compute="_compute_family_history_ids",
        inverse="_inverse_family_history_ids",
    )
    psychobiological_habits_history_ids = fields.One2many(
        "dom.patient.history",
        "patient_id",
        compute="_compute_psychobiological_habits_history_ids",
        inverse="_inverse_psychobiological_habits_history_ids",
    )
    sexual_activity_history_ids = fields.One2many(
        "dom.patient.history",
        "patient_id",
        compute="_compute_sexual_activity_history_ids",
        inverse="_inverse_sexual_activity_history_ids",
    )
    other_history_ids = fields.One2many(
        "dom.patient.history",
        "patient_id",
        compute="_compute_other_history_ids",
        inverse="_inverse_other_history_ids",
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

    @api.depends("history_ids")
    def _compute_personal_history_ids(self):
        self._compute_history_ids("personal")

    @api.depends("history_ids")
    def _inverse_personal_history_ids(self):
        self._inverse_history_ids("personal")

    @api.depends("history_ids")
    def _compute_family_history_ids(self):
        self._compute_history_ids("family")

    @api.depends("history_ids")
    def _inverse_family_history_ids(self):
        self._inverse_history_ids("family")

    @api.depends("history_ids")
    def _compute_psychobiological_habits_history_ids(self):
        self._compute_history_ids("psychobiological_habits")

    @api.depends("history_ids")
    def _inverse_psychobiological_habits_history_ids(self):
        self._inverse_history_ids("psychobiological_habits")

    @api.depends("history_ids")
    def _compute_sexual_activity_history_ids(self):
        self._compute_history_ids("sexual_activity")

    @api.depends("history_ids")
    def _inverse_sexual_activity_history_ids(self):
        self._inverse_history_ids("sexual_activity")

    @api.depends("history_ids")
    def _compute_other_history_ids(self):
        self._compute_history_ids("other")

    @api.depends("history_ids")
    def _inverse_other_history_ids(self):
        self._inverse_history_ids("other")

    def _compute_history_ids(self, history_type):
        """
        Generic funcition for computing history_ids based on history type

        Args:
            history_type (str): One of the options defined in 'type' selection field
            of 'dom.patient.history' model
        """
        for record in self:
            history = record.history_ids.filtered(lambda r: r.type == history_type)
            setattr(record, f"{history_type}_history_ids", history)

    def _inverse_history_ids(self, history_type):
        for record in self:
            new_records = getattr(record, f"{history_type}_history_ids").filtered(
                lambda r: not r.id
            )
            deleted_records = record.history_ids.filtered(
                lambda r: r.type == history_type
            ) - getattr(record, f"{history_type}_history_ids")

            record.history_ids -= deleted_records
            record.history_ids |= new_records
