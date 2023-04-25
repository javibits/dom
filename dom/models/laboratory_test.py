from odoo import _, fields, models


class LaboratoryTest(models.Model):
    _name = "dom.laboratory.test"
    _description = "Laboratory Test"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_laboratory_test_name_unique",
            "UNIQUE (name)",
            _("Test already exists."),
        ),
    ]

    name = fields.Char(string=_("Name"))


class LaboratoryTestProfile(models.Model):
    _name = "dom.laboratory.test.profile"
    _description = "Laboratory Test Profile"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_laboratory_test_profile_name_unique",
            "UNIQUE (name)",
            _("Profile name already exists."),
        ),
    ]

    name = fields.Char(string=_("Name"))
    laboratory_test_ids = fields.Many2many(
        "dom.laboratory.test",
        string=_("Tests"),
        ondelete="restrict",
    )
