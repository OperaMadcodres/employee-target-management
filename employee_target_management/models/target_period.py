from odoo import models, fields


class TargetPeriod(models.Model):
    _name = "employee.target.period"
    _description = "Employee Target Period"
    _order = "date_from desc"

    name = fields.Char(
        string="Period Name",
        required=True
    )

    date_from = fields.Date(
        string="From Date",
        required=True
    )

    date_to = fields.Date(
        string="To Date",
        required=True
    )

    active = fields.Boolean(
        string="Active",
        default=True
    )

    description = fields.Text(
        string="Description"
    )