from odoo import fields, models, api, _
from datetime import date

from odoo.exceptions import UserError


class CustomerContract(models.Model):
    _name = 'customer.contract'
    _description = 'Customer Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', related='partner_id.name', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, track_visibility='onchange',auto_join=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    start_date = fields.Date(string='Start Date', track_visibility='onchange')
    end_date = fields.Date(string='End Date', track_visibility='onchange')
    price = fields.Monetary(string='Price', track_visibility='onchange')
    avg_day_price = fields.Monetary(string='Average Day Price', track_visibility='onchange',compute='_compute_avg_day_price')
    status = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('end', 'Ended'),('cancel','Canceled')], string='Status', track=True, default='draft')
    last_status_changer = fields.Char(string='Last change status by', readonly=True)

    @api.depends('start_date','end_date','price')
    def _compute_avg_day_price(self):
        for record in self:
            try:
                if record.start_date and record.end_date and record.price:
                    record.avg_day_price = record.price / ((record.end_date - record.start_date).days + 1)
                elif record.price <= 0:
                    record.avg_day_price = 0
                else:
                      continue
            except ZeroDivisionError:
                raise UserError(_('you can not divide by zero'))
    @api.onchange('start_date')
    def _empty_end_date(self):
        for record in self:
            if record.start_date and record.end_date:
                record.end_date = False


    def cron_ended_contract(self):
        for record in self:
            if record.end_date < date.today() and record.status == 'confirm':
                record.status = 'end'
            else:
                continue

    def write(self, vals):
        # get the user who change the status
        if 'status' in vals:
            vals['last_status_changer'] = self.env.user.name
        return super(CustomerContract, self).write(vals)
