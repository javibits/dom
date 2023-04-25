from odoo import _, fields, models


class Medicine(models.Model):
    _name = "dom.medicine"
    _description = "Medicine"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_medicine_name_presentation_unique",
            "UNIQUE (name, presentation)",
            _("Medicine already exists."),
        ),
    ]

    name = fields.Char(string=_("Name"))
    presentation = fields.Char(string=_("Presentation"))
    directions = fields.Text(string=_("Directions"))

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, f"{record.name} / {record.presentation}"))
        return res


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
