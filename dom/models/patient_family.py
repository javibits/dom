from odoo import _, fields, models


class PatientFamily(models.Model):
    _name = "dom.patient.family"
    _description = "Patient Family"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_patient_family_name_unique",
            "UNIQUE (name)",
            _("Relationship already exists."),
        ),
    ]

    name = fields.Char(string=_("Relationship"))
