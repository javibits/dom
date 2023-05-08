from odoo import _, fields, models


class LaboratoryTestOrderLine(models.Model):
    _name = "dom.laboratory.test.order.line"
    _description = "Laboratory Test Order Line"
    _rec_name = "laboratory_test_id"

    laboratory_test_order_id = fields.Many2one(
        "dom.laboratory.test.order",
        string=_("Laboratory Test Order"),
        ondelete="cascade",
    )
    laboratory_test_id = fields.Many2one(
        "dom.laboratory.test", string=_("Name"), ondelete="restrict"
    )


class LaboratoryTestOrder(models.Model):
    _name = "dom.laboratory.test.order"
    _inherit = ["dom.order.abstract"]
    _description = "Laboratory Test Order"
    order = "date desc, pacient_id asc"
    _sql_constraints = [
        (
            "dom_patient_date_unique",
            "UNIQUE (patient_id, date)",
            _("A patient already has a Laboratory Test Order on this date"),
        ),
        (
            "dom_patient_appointment_unique",
            "UNIQUE (appointment_id)",
            _("Appointment already has a Laboratory Test Order"),
        ),
    ]

    line_ids = fields.One2many(
        "dom.laboratory.test.order.line",
        "laboratory_test_order_id",
        string=_("Tests"),
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
