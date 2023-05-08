from odoo import _, api, fields, models


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
    _description = "Referral Order"
    _order = "date desc, patient_id asc"

    _sql_constraints = [
        (
            "dom_date_patient_doctor_unique",
            "UNIQUE (date, patient_id, doctor_id)",
            _("Referral order already exists."),
        ),
    ]

    date = fields.Date(
        string=_("Date"),
        default=fields.Date.context_today,
        readonly=True,
    )
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
    patient_id = fields.Many2one(
        "res.partner",
        string=_("Patient"),
        ondelete="cascade",
        compute="_compute_patient_id_onchange",
        store=True,
        readonly=False,
        required=True,
        domain=[("is_patient", "=", True)],
    )
    appointment_id = fields.Many2one(
        "dom.patient.appointment",
        string=_("Appointment"),
        ondelete="cascade",
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

    @api.depends("appointment_id")
    def _compute_patient_id_onchange(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
        else:
            self.patient_id = None
