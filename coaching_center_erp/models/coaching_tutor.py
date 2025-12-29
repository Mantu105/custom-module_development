from odoo import models, fields,api
from odoo.exceptions import ValidationError

class CoachingTutor(models.Model):
    _name = 'coaching.tutor'
    _description = 'Tutor / Instructor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='active', tracking=True)
    batch_id = fields.Many2one('coaching.batch', string='Batch', ondelete='set null', help="Link to a batch taught by this tutor")
    subject_ids = fields.Many2many('coaching.subject', string='Subjects', help="Subjects taught by this tutor")
    batch_count = fields.Integer(string="Batch Count", compute='_compute_batch_count')
    batch_assignment_ids = fields.One2many('coaching.tutor.assignment','tutor_id',string="Batch Assignments")
    notes = fields.Html(string='Notes / Experience')
    def _compute_batch_count(self):
        for tutor in self:
            tutor.batch_count = len(tutor.batch_assignment_ids) if tutor.batch_assignment_ids else 0

    def action_open_batches(self):
        return {
        'name': 'Assigned Batches',
        'type': 'ir.actions.act_window',
        'res_model': 'coaching.batch',
        'view_mode': 'list,form',
        'domain': [('id', 'in', self.batch_assignment_ids.mapped('batch_id').ids)],
        'context': {'default_tutor_id': self.id},
        'target': 'current',
        }
    
    @api.constrains('email', 'phone')
    def _check_unique_email_phone(self):
        for rec in self:
            if rec.email:
                existing_email = self.env['coaching.tutor'].search([
                    ('email', '=', rec.email),
                    ('id', '!=', rec.id)
                ], limit=1)
                if existing_email:
                    raise ValidationError(f"Email '{rec.email}' is already registered for another tutor.")
            if rec.phone:
                existing_phone = self.env['coaching.tutor'].search([
                    ('phone', '=', rec.phone),
                    ('id', '!=', rec.id)
                ], limit=1)
                if existing_phone:
                    raise ValidationError(f"Phone '{rec.phone}' is already registered for another tutor.") 
