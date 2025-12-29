from odoo import models, fields
from odoo.exceptions import UserError

class CoachingInquiry(models.Model):
    _name = "coaching.inquiry"
    _description = "Student Inquiry"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True)
    mobile = fields.Char("Mobile Number", required=True)
    email = fields.Char("Email")
    inquiry_date = fields.Date("Inquiry Date", default=fields.Date.today)
    
    interested_course_id = fields.Many2one("coaching.course", string="Interested Course")
    interested_batch_id = fields.Many2one("coaching.batch", string="Interested Batch")
    
    notes = fields.Text("Remarks")
    status = fields.Selection([
        ('new', 'New'),
        ('followup', 'Follow-Up'),
        ('registered', 'Registered'),
        ('dropped', 'Dropped')
    ], default='new', string="Status", tracking=True)




