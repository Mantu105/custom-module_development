from odoo import models, fields, api,_
from datetime import date
from odoo.exceptions import ValidationError

class CoachingFee(models.Model):
    _name = 'coaching.fee'
    _description = 'Student Coaching Fee'
    _rec_name = 'student_id'
    _order = 'payment_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    student_id = fields.Many2one('coaching.student', string='Student', required=True, ondelete='cascade')
    batch_id = fields.Many2one('coaching.batch', string='Batch', required=True  )
    amount = fields.Float(string='Total Fee Amount', compute='_compute_amount_from_batch', store=True, readonly=True, tracking=True)
    total_paid_so_far = fields.Float(string='Total Previous Paid', compute='_compute_total_paid_so_far', store=True, readonly=True, tracking=True)
    amount_paid = fields.Float(string='Amount Paid', required=True,tracking=True)
    balance = fields.Float(string='Pending Balance', compute='_compute_balance', store=True, tracking=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.today)
    payment_mode = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ], string='Payment Mode', required=True)
    notes = fields.Text(string='Notes')
    status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], string='Status', compute='_compute_status', store=True)

    @api.depends('amount', 'amount_paid', 'total_paid_so_far')
    def _compute_balance(self):
        for record in self:
            paid_total = record.total_paid_so_far + record.amount_paid
            record.balance = record.amount - paid_total

    @api.depends('balance', 'amount_paid')
    def _compute_status(self):
        for record in self:
            if record.amount_paid == 0:
                record.status = 'unpaid'
            elif record.balance <= 0:
                record.status = 'paid'
            elif 0 < record.balance < record.amount:
                record.status = 'partial'
            else:
                record.status = 'unpaid'

    @api.depends('batch_id')
    def _compute_amount_from_batch(self):
        for record in self:
            record.amount = record.batch_id.amount if record.batch_id else 0.0

    @api.depends('student_id', 'batch_id')
    def _compute_total_paid_so_far(self):
        for record in self:
            if record.student_id and record.batch_id:
                domain = [
                    ('student_id', '=', record.student_id.id),
                    ('batch_id', '=', record.batch_id.id),
                    ('id', '!=', record.id)
                ]
                past_payments = self.search(domain)
                record.total_paid_so_far = sum(p.amount_paid for p in past_payments)
            else:
                record.total_paid_so_far = 0.0

    @api.constrains('amount_paid', 'total_paid_so_far', 'amount')
    def _check_overpayment(self):
        for record in self:
            if record.total_paid_so_far + record.amount_paid > record.amount:
                raise ValidationError(_("Overpayment: This payment exceeds the total batch fee. Please enter only pending amount."))
                  
            
    @api.constrains('student_id', 'batch_id')
    def _check_already_paid(self):
        for record in self:
            if record.student_id and record.batch_id:
                domain = [
                    ('student_id', '=', record.student_id.id),
                    ('batch_id', '=', record.batch_id.id),
                    ('id', '!=', record.id)
                ]
                existing_payments = self.search(domain)
                total_paid = sum(p.amount_paid for p in existing_payments)
                if total_paid >= record.batch_id.amount:
                    raise ValidationError(_("This student has already paid full fees for this batch."))

    @api.onchange('student_id')
    def _onchange_student_id(self):
        if self.student_id:
            self.batch_id = self.student_id.batch_id


    # @api.model
    # def get_batch_wise_data(self):
    #     batches = self.search([])
    #     result = []
    #     for batch in batches:
    #         student_ids = self.env['coaching.student'].search([('batch_id', '=', batch.id)])
    #         student_ids_list = student_ids.ids

    #         # Get total fee paid for this batch
    #         fee_records = self.env['coaching.fee'].search([('batch_id', '=', batch.id)])
    #         total_revenue = sum(fee_records.mapped('amount_paid'))

    #         result.append({
    #             'batch_name': batch.name,
    #             'total_students': len(student_ids_list),
    #             'total_revenue': total_revenue,
    #         })
    #     return result        
            