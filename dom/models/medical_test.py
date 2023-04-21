from odoo import _, fields, models


class MedicalTest(models.Model):
    _name = "dom.medical.test"
    _description = "Medical Test"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_medical_test_name_unique",
            "UNIQUE (name)",
            _("Test already exists."),
        ),
    ]

    name = fields.Char(string=_("Name"))


class MedicalTestProfile(models.Model):
    _name = "dom.medical.test.profile"
    _description = "Medical Test Profile"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_medical_test_profile_name_unique",
            "UNIQUE (name)",
            _("Profile name already exists."),
        ),
    ]

    name = fields.Char(string=_("Name"))
    medical_test_ids = fields.Many2many("dom.medical.test", string=_("Tests"))
