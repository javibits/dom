from odoo import _, fields, models


class ReferralDoctor(models.Model):
    _inherit = "res.partner"
    _order = "name asc"

    is_doctor = fields.Boolean(
        string=_("Is a Doctor?"),
        default=False,
    )
    specialization_id = fields.Many2one(
        "dom.doctor.specialization",
        string=_("Specialization"),
        ondelete="restrict",
    )

    def name_get(self):
        res = []
        for record in self:
            if record.is_doctor:
                res.append(
                    (record.id, f"{record.name} / {record.specialization_id.name}")
                )
            else:
                res.append((record.id, f"{record.name}"))
        return res


class ReferralOrder(models.Model):
    _name = "dom.referral.order"
    _inherit = ["dom.order.abstract"]
    _description = "Referral Order"
    _order = "date desc, patient_id asc"

    _sql_constraints = [
        (
            "dom_date_patient_doctor_unique",
            "UNIQUE (date, patient_id, doctor_id)",
            _("Referral order already exists."),
        ),
    ]

    doctor_id = fields.Many2one(
        "res.partner",
        string=_("Doctor"),
        domain="[('is_doctor','=',True)]",
        required=True,
        ondelete="restrict",
    )
    specialization_id = fields.Many2one(
        "dom.doctor.specialization",
        related="doctor_id.specialization_id",
    )
    note = fields.Text(string=_("Note"))

    def name_get(self):
        res = []
        for record in self:
            res.append(
                (
                    record.id,
                    f"{record.date}: {record.patient_id.name} - {record.specialization_id.name}",
                )
            )
        return res
