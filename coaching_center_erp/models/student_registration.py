from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StudentRegistration(models.Model):
    _name = 'coaching.student'
    _description = 'Student Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Full Name', required=True)
    student_id = fields.Char(string='Student ID', readonly=True, copy=False, index=True, default='New')
    dob = fields.Date(string='Date of Birth')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    guardian_name = fields.Char(string='Guardian Name')
    guardian_phone = fields.Char(string='Guardian Phone')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    country_code = fields.Char(related='country_id.code', string="Country Code")
    photo = fields.Image("Photo", max_width=1920, max_height=1920)
    batch_id = fields.Many2one('coaching.batch', string='Batch', ondelete='set null')
    batch_name = fields.Char(related='batch_id.name', string='Batch Name', store=True)
    batch_start_date = fields.Date(related='batch_id.start_date', string='Start Date')
    batch_end_date = fields.Date(related='batch_id.end_date', string='End Date')
    batch_timing = fields.Char(related='batch_id.timing', string='Timing')
    admission_date = fields.Date(string='Admission Date', default=fields.Date.today())
    status = fields.Selection([
        ('active', 'Active'),
        ('left', 'Left'),
        ('completed', 'Completed')
    ], string='Status', default='active', tracking=True)
    fee_ids = fields.One2many('coaching.fee', 'student_id', string='Fee Records')

    @api.model
    def create(self, vals):
        if vals.get('student_id', 'New') == 'New':
            new_id = self.env['ir.sequence'].next_by_code('coaching.student') or '/'
            vals['student_id'] = new_id
        return super(StudentRegistration, self).create(vals)

    @api.constrains('email', 'phone')
    def _check_duplicate_email_phone(self):
        for record in self:
            domain = ['|', ('email', '=', record.email), ('phone', '=', record.phone)]
            domain += [('id', '!=', record.id)]
            existing = self.search(domain, limit=1)
            if existing:
                raise ValidationError("This student is already registered with the same email or phone number.") 

        
