from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import AccessError


class EmployeeTarget(models.Model):
    _name = "employee.target"
    _description = "Employee Target"
    _order = "date_from desc"

    name = fields.Char(
        string="Target",
        required=True
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True
    )

    target_type_id = fields.Many2one(
        "employee.target.type",
        string="Target Type",
        required=True
    )

    period_id = fields.Many2one(
        "employee.target.period",
        string="Period",
        required=True
    )

    date_from = fields.Date(
        string="From Date",
        related="period_id.date_from",
        store=True
    )

    date_to = fields.Date(
        string="To Date",
        related="period_id.date_to",
        store=True
    )

    target_value = fields.Float(
        string="Target Value",
        required=True
    )

    achieved_value = fields.Float(
        string="Achieved",
        default=0.0,
        readonly=True
    )

    progress = fields.Float(
        string="Progress %",
        compute="_compute_progress",
        store=True
    )

    active = fields.Boolean(
        string="Active",
        default=True
    )

    status = fields.Selection(
    selection=[
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ],
    string="Status",
    default="draft",
    required=True,
    )

    notes = fields.Text(
        string="Notes"
    )

    @api.depends("target_value", "achieved_value")
    def _compute_progress(self):
        for record in self:
            if record.target_value > 0:
                record.progress = (
                    record.achieved_value / record.target_value
                ) * 100
            else:
                record.progress = 0.0

    def action_calculate_achievement(self):
        for record in self:

            record.achieved_value = 0.0

            if not record.employee_id.user_id:
                continue

            source = record.target_type_id.achievement_source
            measurement = record.target_type_id.measurement_type

            # ============================================================
            # SALES
            # ============================================================

            if source == "sales":

                orders = self.env["sale.order"].search([
                    ("user_id", "=", record.employee_id.user_id.id),
                    ("state", "in", ["sale", "done"]),
                    ("date_order", ">=", record.date_from),
                    ("date_order", "<=", record.date_to),
                ])

                if measurement == "amount":

                    record.achieved_value = sum(
                        orders.mapped("amount_total")
                    )

                elif measurement == "quantity":

                    total_quantity = 0.0

                    for order in orders:
                        for line in order.order_line:
                            total_quantity += line.product_uom_qty

                    record.achieved_value = total_quantity

                elif measurement == "count":

                    record.achieved_value = len(orders)

            # ============================================================
            # COLLECTION
            # ============================================================

            elif source == "collection":

                payments = self.env["account.payment"].search([
                    ("state", "=", "paid"),
                    ("date", ">=", record.date_from),
                    ("date", "<=", record.date_to),
                ])

                total_collection = 0.0
                payment_count = 0

                for payment in payments:

                    invoices = payment.reconciled_invoice_ids.filtered(
                        lambda invoice:
                            invoice.move_type == "out_invoice"
                            and invoice.invoice_user_id.id
                            == record.employee_id.user_id.id
                    )

                    if not invoices:
                        continue

                    if measurement == "amount":
                        total_collection += payment.amount

                    elif measurement == "count":
                        payment_count += 1

                if measurement == "amount":
                    record.achieved_value = total_collection

                elif measurement == "count":
                    record.achieved_value = payment_count

            # ============================================================
            # CUSTOMER
            # ============================================================

            elif source == "customer":

                customers = self.env["res.partner"].search([
                    ("create_uid", "=", record.employee_id.user_id.id),
                    ("create_date", ">=", record.date_from),
                    ("create_date", "<=", record.date_to),
                    ("customer_rank", ">", 0),
                ])

                if measurement == "count":
                    record.achieved_value = len(customers)

            # ============================================================
            # UPDATE PROGRESS / STATUS
            # ============================================================

            if record.target_value > 0:
                record.progress = (
                    record.achieved_value / record.target_value
                ) * 100
            else:
                record.progress = 0.0

            # Automatically complete the target
            if (
                record.status == "active"
                and record.target_value > 0
                and record.achieved_value >= record.target_value
            ):
                record.status = "completed"

            

    def action_submit(self):
        for record in self:
            if record.status == "draft":
                record.status = "submitted"

    def action_approve(self):

        if not self.env.user.has_group(
        "employee_target_management.group_employee_target_manager"
        ):
            raise AccessError(
                "Only Target Managers can approve targets."
            )
    
        for record in self:
            if record.status == "submitted":
                record.status = "approved"

    def action_activate(self):

        if not self.env.user.has_group(
                "employee_target_management.group_employee_target_manager"
                ):
                    raise AccessError(
                        "Only Target Managers can approve targets."
                    )
        
        for record in self:
            if record.status == "approved":
                record.status = "active"

    def action_complete(self):

        if not self.env.user.has_group(
                "employee_target_management.group_employee_target_manager"
                ):
                    raise AccessError(
                        "Only Target Managers can approve targets."
                    )
        
        for record in self:
            if record.status == "active":
                record.status = "completed"

    def action_cancel(self):

        if not self.env.user.has_group(
                "employee_target_management.group_employee_target_manager"
                ):
                    raise AccessError(
                        "Only Target Managers can approve targets."
                    )
        
        for record in self:
            if record.status != "completed":
                record.status = "cancelled"

    def action_reset_to_draft(self):

        if not self.env.user.has_group(
                "employee_target_management.group_employee_target_manager"
                ):
                    raise AccessError(
                        "Only Target Managers can approve targets."
                    )
        
        for record in self:
            if record.status in ("cancelled", "submitted"):
                record.status = "draft"

    @api.constrains(
    "employee_id",
    "target_type_id",
    "period_id"
)
    def _check_duplicate_target(self):

        for record in self:

            duplicate = self.search([
                ("id", "!=", record.id),
                ("employee_id", "=", record.employee_id.id),
                ("target_type_id", "=", record.target_type_id.id),
                ("period_id", "=", record.period_id.id),
            ], limit=1)

            if duplicate:
                raise ValidationError(
                    "A target already exists for this employee, "
                    "target type and period."
                )
            
    @api.model
    def get_dashboard_employees(self):
        """Return employees available for the dashboard."""

        if self.env.user.has_group(
            "employee_target_management.group_employee_target_manager"
        ):
            employees = self.env["hr.employee"].search([
                ("active", "=", True),
            ])
        else:
            employees = self.env["hr.employee"].search([
                ("active", "=", True),
                ("user_id", "=", self.env.user.id),
            ])

        return employees.read(["id", "name"])