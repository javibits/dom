from odoo import _, fields, models


class PatientDiagnosis(models.Model):
    _name = "dom.patient.diagnosis"
    _description = "Patient Diagnosis"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_patient_diagnosis_name_unique",
            "UNIQUE (name)",
            _("Diagosis already exists."),
        ),
    ]

    name = fields.Char(string=_("Diagnosis"))
