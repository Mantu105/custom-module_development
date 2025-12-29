from odoo import models, fields

class CoachingCourse(models.Model):
    _name = 'coaching.course'
    _description = 'Coaching Course'

    name = fields.Char(string='Course Name', required=True)


class CoachingSubject(models.Model):
    _name = 'coaching.subject'
    _description = 'Coaching Subject'

    name = fields.Char(string='Subject Name', required=True)