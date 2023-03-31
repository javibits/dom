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
