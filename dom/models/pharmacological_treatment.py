from odoo import _, fields, models


class PharmacologicalTreatment(models.Model):
    _name = "dom.pharmacological.treatment"
    _description = "Pharmacological treatment"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_pharmacological_treatment_name_unique",
            "UNIQUE (name)",
            _("Pharmacological Treatment already exists."),
        ),
    ]

    name = fields.Char(string=_("Name"))
    medicine_ids = fields.Many2many(
        "dom.medicine",
        string=_("Medicines"),
        ondelete="restrict",
    )
