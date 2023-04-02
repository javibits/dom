from odoo import _, fields, models


class PatientHistory(models.Model):
    _name = "dom.patient.history"
    _description = "Patient History"

    name = fields.Char(string=_("Name"))
    type = fields.Selection(
        [
            ("personal", _("Personal")),
            ("relative", _("Relative")),
            ("psychobiological_habits", _("Psychobiological Habits")),
            ("sexual_activity", _("Sexual Activity")),
            ("other", _("Other")),
        ],
        string=_("Type"),
        required=True,
    )
    note = fields.Char(string=_("Note"))
    patient_id = fields.Many2one("res.partner", string=_("Patient"), ondelete="cascade")
