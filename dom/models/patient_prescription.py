from odoo import _, api, fields, models


class PatientPrescriptionLine(models.Model):
    _name = "dom.patient.prescription.line"
    _description = "Patient Prescription Line"
    _rec_name = "medicine_id"

    prescription_id = fields.Many2one(
        "dom.patient.prescription",
        string=_("Prescription"),
        ondelete="cascade",
    )
    medicine_id = fields.Many2one(
        "dom.medicine", string=_("Medicine"), ondelete="restrict"
    )
    directions = fields.Text(
        string=_("Directions"),
        compute="_compute_directions_onchange",
        store=True,
        readonly=False,
    )

    @api.depends("medicine_id")
    def _compute_directions_onchange(self):
        if self.medicine_id:
            self.directions = self.medicine_id.directions
        else:
            self.directions = ""


class PatientPrescription(models.Model):
    _name = "dom.patient.prescription"
    _description = "Patient Prescription"
    order = "date desc, pacient_id asc"
    _sql_constraints = [
        (
            "dom_patient_name_unique",
            "UNIQUE (patient_id, date)",
            _("A patient already has a prescription on this date"),
        ),
        (
            "dom_patient_appointment_unique",
            "UNIQUE (appointment_id)",
            _("Appointment already has a prescription."),
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
    line_ids = fields.One2many(
        "dom.patient.prescription.line",
        "prescription_id",
        string=_("Medicines"),
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