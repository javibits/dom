from odoo import _, fields, models


class PatientAppointmentReason(models.Model):
    _name = "dom.patient.appointment.reason"
    _description = "Patient Appointment Reason"
    order = "name asc"

    name = fields.Char(string=_("Reason"))
