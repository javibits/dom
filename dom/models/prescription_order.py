from odoo import _, api, fields, models


class PrescriptionOrderLine(models.Model):
    _name = "dom.prescription.order.line"
    _description = "Prescription Order Line"
    _rec_name = "medicine_id"

    prescription_order_id = fields.Many2one(
        "dom.prescription.order",
        string=_("Prescription"),
        ondelete="cascade",
    )
    medicine_id = fields.Many2one(
        "dom.medicine",
        string=_("Name"),
        ondelete="restrict",
    )
    directions = fields.Text(
        string=_("Directions"),
        compute="_compute_directions_onchange",
        store=True,
        readonly=False,
    )

    @api.depends("medicine_id")
    def _compute_directions_onchange(self):
        for line in self:
            if line.medicine_id:
                line.directions = line.medicine_id.directions
            else:
                line.directions = ""


class PrescriptionOrder(models.Model):
    _name = "dom.prescription.order"
    _inherit = ["dom.order.abstract"]
    _description = "Prescription Order"
    order = "date desc, pacient_id asc"
    _sql_constraints = [
        (
            "dom_patient_name_unique",
            "UNIQUE (patient_id, date)",
            _("A patient already has a Prescription Order on this date"),
        ),
        (
            "dom_patient_appointment_unique",
            "UNIQUE (appointment_id)",
            _("Appointment already has a Prescription Order"),
        ),
    ]

    pharmacological_treatment_ids = fields.Many2many(
        "dom.pharmacological.treatment",
        related="appointment_id.pharmacological_treatment_ids",
        readonly=False,
    )
    line_ids = fields.One2many(
        "dom.prescription.order.line",
        "prescription_order_id",
        string=_("Medicines"),
    )

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
