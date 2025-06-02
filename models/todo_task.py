from email.policy import default

from odoo import models , fields , api
from odoo.exceptions import ValidationError

class ToDoTask(models.Model):
    _name = 'todo.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Task'

    name = fields.Char('Task Name' , default = "Task ")
    due_date = fields.Date()
    is_late = fields.Boolean(default=False)
    description = fields.Text()
    assign_to_id = fields.Many2one('res.partner')
    state = fields.Selection([
                            ('new', 'New'),
                            ('in_progress', 'In Progress'),
                            ('completed', 'Completed'),
                            ('closed','Closed')
                            ] , default = "new")
    active = fields.Boolean(default=True)
    estimated_time = fields.Float()
    line_ids = fields.One2many('todo.task.line' , 'task_id')
    total_logged_time = fields.Float(string="Total Time Taken", compute="_compute_total_time", store=True)

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

    def action_closed(self):
        for rec in self:
            rec.state = 'closed'

    def check_due_date(self):
        tasks_ids = self.search([])
        for rec in tasks_ids:
            if rec.due_date and rec.state not in ['completed' , 'closed'] and rec.due_date < fields.date.today():
                rec.is_late = True
            else:
                rec.is_late = False


    @api.depends('line_ids.time')
    def _compute_total_time(self):
        for task in self:
            task.total_logged_time = sum(task.line_ids.mapped('time'))

    formatted_total_time = fields.Char(
        string="Total Time (HH:MM)",
        compute="_compute_formatted_total_time"
    )

    @api.depends('total_logged_time')
    def _compute_formatted_total_time(self):
        for rec in self:
            hours = int(rec.total_logged_time)
            minutes = int(round((rec.total_logged_time - hours) * 60))
            rec.formatted_total_time = f"{hours}:{minutes:02d}"


class ToDoTaskLine(models.Model):
    _name = "todo.task.line"

    task_id = fields.Many2one('todo.task')
    description = fields.Char(default="Rec ")
    date = fields.Date(default=fields.Date.today())
    time = fields.Float(string='Time (Hours)' , required=True)

    @api.constrains('time')
    def _check_total_time(self):
        for rec in self:
            total_time = sum(rec.task_id.line_ids.mapped('time'))
            if total_time > rec.task_id.estimated_time:
                raise ValidationError("Total time can not be greater than estimated time")


