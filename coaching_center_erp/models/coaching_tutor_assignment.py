from odoo import models, fields
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class CoachingTutorAssignment(models.Model):
    _name = 'coaching.tutor.assignment'
    _description = 'Tutor Assignment to Batch by Day'
    _rec_name = 'tutor_id'

    tutor_id = fields.Many2one('coaching.tutor', string="Tutor", required=True)
    batch_id = fields.Many2one('coaching.batch', string="Batch", required=True)
    day = fields.Selection([
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday')
    ], string="Day", required=True)
    session_datetime = fields.Datetime(string="Session Start Time", required=True)
    duration_hours = fields.Float(string="Duration (Hours)", default=1.0)

    @api.constrains('tutor_id', 'batch_id', 'session_datetime', 'duration_hours')
    def _check_overlap_sessions(self):
        for rec in self:
            session_start = rec.session_datetime
            session_end = session_start + timedelta(hours=rec.duration_hours)

            domain = [
                ('id', '!=', rec.id),
                ('session_datetime', '<', session_end),
            ]

            tutor_overlap = self.env['coaching.tutor.assignment'].search(
                domain + [
                    ('tutor_id', '=', rec.tutor_id.id),
                    ('session_datetime', '>=', session_start - timedelta(hours=12))
                ]
            ).filtered(lambda r: (
                r.session_datetime + timedelta(hours=r.duration_hours) > session_start
            ))

            if tutor_overlap:
                raise ValidationError(_(
                    f"Tutor '{rec.tutor_id.name}' has overlapping sessions at {session_start.strftime('%Y-%m-%d %H:%M')}."
                ))

            batch_overlap = self.env['coaching.tutor.assignment'].search(
                domain + [
                    ('batch_id', '=', rec.batch_id.id),
                    ('session_datetime', '>=', session_start - timedelta(hours=12))
                ]
            ).filtered(lambda r: (
                r.session_datetime + timedelta(hours=r.duration_hours) > session_start
            ))

            if batch_overlap:
                raise ValidationError(_(
                    f"Batch '{rec.batch_id.name}' already has a tutor assigned during this time."
                ))
