from odoo import _, fields, models


HISTORY_TYPE_SELECTION_VALUES = [
    ("personal", _("Personal")),
    ("family", _("Family")),
    ("psychobiological_habits", _("Psychobiological Habits")),
    ("sexual_activity", _("Sexual Activity")),
    ("other", _("Other")),
]


class PatientHistoryItem(models.Model):
    _name = "dom.patient.history.item"
    _description = "Patient History Item"
    _rec_name = "item"

    item = fields.Char(
        string=_("Item"),
        help=_(
            "Indicate the desease, condition, habit or activity depending on the type. "
            "'Personal' and 'Family' type items are shared"
        ),
    )
    type = fields.Selection(
        HISTORY_TYPE_SELECTION_VALUES,
        string=_("Type"),
        required=True,
    )


class PatientHistory(models.Model):
    _name = "dom.patient.history"
    _description = "Patient History"
    _rec_name = "item_id"

    item_id = fields.Many2one(
        "dom.patient.history.item",
        string=_("Name"),
        ondelete="restrict",
    )

    patient_id = fields.Many2one(
        "res.partner",
        string=_("Patient"),
        ondelete="cascade",
    )
    type = fields.Selection(
        HISTORY_TYPE_SELECTION_VALUES,
        string=_("Type"),
        required=True,
    )
    note = fields.Text(string=_("Note"))
    important = fields.Boolean(string=_("Is important?"))

    # Only for 'family' type
    family_id = fields.Many2one(
        "dom.patient.family",
        string=_("Relationship"),
        ondelete="restrict",
    )
    family_deceased = fields.Boolean(string=_("Deceased?"))

    def write(self, vals):
        """
        Only saves the record if there are actual values to update
        When there are no values to update, vals only contains patient_id
        This is done to prevent changing write_date of these records when
        performing operations to_history_ids records in Patient form
        """
        vals.pop("patient_id", False)
        if vals:
            res = super().write(vals)
            return res
