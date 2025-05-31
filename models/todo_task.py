from odoo import models , fields , api
from odoo.exceptions import ValidationError

class ToDoTask(models.Model):
    _name = 'todo.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Task'

    name = fields.Char('Task Name' , default = "Task ")
    due_date = fields.Date()
    description = fields.Text()
    assign_to_id = fields.Many2one('res.partner')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ] , default = "new")

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Task name must be unique')
    ]

    def action_new(self):
        for rec in self:
            rec.state = 'new'

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_completed(self):
        for rec in self:
            rec.state = 'completed'

    @api.constrains('assign_to_id')
    def _check_assign_to_id(self):
        for rec in self:
            if not rec.assign_to_id:
                raise ValidationError("Please Choose A Partner To Assign The Task To")