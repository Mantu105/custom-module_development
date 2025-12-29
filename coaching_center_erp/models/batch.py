from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class CoachingBatch(models.Model):
    _name = 'coaching.batch'
    _description = 'Coaching Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Batch Name', required=True, help="e.g. 'Morning 9-11'")
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date')
    timing = fields.Char(string='Timing', help="e.g. '9 AM - 11 AM'")
    student_ids = fields.One2many('coaching.student','batch_id', string='Students in Batch')
    student_count = fields.Integer(string='Student Count',compute='_compute_student_count')
    student_id = fields.Many2one('coaching.student', string='Student', ondelete='set null', help="Link to a student in this batch")
    amount = fields.Float(string='Batch Fee Amount', required=True, help="Default fee amount for this batch")
    tutor_id = fields.Many2one('coaching.tutor', string='Assigned Tutor')
    course_id = fields.Many2one('coaching.course', string='Course', required=True, help="Course associated with this batch")
    tutor_ids = fields.One2many(string="Tutors", comodel_name='coaching.tutor', inverse_name='batch_id', help="Tutors assigned to this batch")
    tutor_assignment_ids = fields.One2many('coaching.tutor.assignment', 'batch_id', string="Tutor Assignments")
    total_amount_collected = fields.Float(string="Total Amount Collected", compute="_compute_total_amount_collected", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='draft', tracking=True, help="Current status of the batch")
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for batch in self:
            if batch.end_date and batch.end_date < batch.start_date:
                raise ValidationError(_("End date cannot be before start date"))

    def _compute_student_count(self):
        for batch in self:
            batch.student_count = len(batch.student_ids)


    def action_view_students(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'coaching.student',
            'view_mode': 'list,form',
            'domain': [('batch_id', '=', self.id)],
            'context': {'default_batch_id': self.id},
        }
    def action_mark_completed(self):
        return {
            "name": "Update Batch",
            "type": "ir.actions.act_window",
            "res_model": "batch.update.wizard",
            "view_mode": "form",
            "target": "new",
        }

    @api.depends('student_ids.fee_ids')
    def _compute_total_amount_collected(self):
        for batch in self:
            total = 0.0
            for student in batch.student_ids:
                for fee in student.fee_ids:
                    if fee.batch_id.id == batch.id:
                        total += fee.amount_paid
            batch.total_amount_collected = total 
                