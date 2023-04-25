from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    gynecological_evaluation = fields.Boolean(
        string=_("Gynecological Evaluation"),
        config_parameter="dom.gynecological_evaluation",
        default=False,
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].set_param(
            "dom.gynecological_evaluation", self.gynecological_evaluation
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            gynecological_evaluation=params.get_param("dom.gynecological_evaluation")
        )
        return res
