from odoo import _, api, fields, models


class MedicalTestOrderLine(models.Model):
    _name = "dom.medical.test.order.line"
    _description = "Medical Test Order Line"
    _rec_name = "medical_test_id"

    medical_test_order_id = fields.Many2one(
        "dom.medical.test.order",
        string=_("Medical Test Order"),
        ondelete="cascade",
    )
    medical_test_id = fields.Many2one(
        "dom.medical.test", string=_("Name"), ondelete="restrict"
    )


class MedicalTestOrder(models.Model):
    _name = "dom.medical.test.order"
    _description = "Medical Test Order"
    order = "date desc, pacient_id asc"
    _sql_constraints = [
        (
            "dom_patient_date_unique",
            "UNIQUE (patient_id, date)",
            _("A patient already has a Medical Test Order on this date"),
        ),
        (
            "dom_patient_appointment_unique",
            "UNIQUE (appointment_id)",
            _("Appointment already has a Medical Test Order"),
        ),
    ]

    date = fields.Date(
        string=_("Date"),
        default=fields.Date.context_today,
        readonly=True,
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
    clinical_summary = fields.Text(string=_("Clinical summary"))
    line_ids = fields.One2many(
        "dom.medical.test.order.line",
        "medical_test_order_id",
        string=_("Tests"),
    )

    @api.depends("appointment_id")
    def _compute_patient_id_onchange(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
        else:
            self.patient_id = None

    def name_get(self):
        res = []
        for record in self:
            res.append(
                (
                    record.id,
                    f"{record.date} - {record.patient_id.sequence} {record.patient_id.name}",
                )
            )
        return res
