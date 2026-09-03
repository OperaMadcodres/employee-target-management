from odoo import models, fields


class TargetType(models.Model):
    _name = "employee.target.type"
    _description = "Employee Target Type"
    _order = "name"

    name = fields.Char(
        string="Target Type",
        required=True
    )

    code = fields.Char(
        string="Code",
        required=True
    )

    measurement_type = fields.Selection(
        selection=[
            ("amount", "Amount"),
            ("quantity", "Quantity"),
            ("count", "Count"),
        ],
        string="Measurement",
        required=True,
        default="amount",
    )

    achievement_source = fields.Selection(
        selection=[
            ("sales", "Sales"),
            ("collection", "Collection"),
            ("customer", "Customer"),
        ],
        string="Achievement Source",
        required=True,
        default="sales",
    )

    description = fields.Text(
        string="Description"
    )

    active = fields.Boolean(
        string="Active",
        default=True
    )