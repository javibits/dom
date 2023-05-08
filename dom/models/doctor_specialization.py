from odoo import _, fields, models


class DoctorSpecialization(models.Model):
    _name = "dom.doctor.specialization"
    _description = "Doctor Specialization"
    _order = "name asc"

    _sql_constraints = [
        (
            "dom_doctor_specialization_name_unique",
            "UNIQUE (name)",
            _("Specialty already exists."),
        ),
    ]
    name = fields.Char(string=_("Name"), required=True)
