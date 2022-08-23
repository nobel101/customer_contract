from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    contract_ids = fields.One2many('customer.contract', 'partner_id', string='Contracts')
    total_contract_prices = fields.Monetary(string='Total Contract Prices', compute='_compute_total_contract_prices')

    @api.depends('contract_ids')
    def _compute_total_contract_prices(self):
        for record in self:
            record.total_contract_prices = self.env['customer.contract'].search([('partner_id', '=', record.id), ('status', '=', 'confirm')]).price

    def action_customer_confirmed_contract(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("customer_contract.customer_contract_win_action")
        action['domain'] = [('partner_id', '=', self.id), ('status', '=', 'confirm')]
        return action
