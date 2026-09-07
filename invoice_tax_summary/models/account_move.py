from markupsafe import Markup, escape

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    tax_summary_html = fields.Html(
        string="Tax Summary",
        compute="_compute_tax_summary_html",
        sanitize=False,
    )

    @api.depends(
    "line_ids.display_type",
    "line_ids.tax_line_id",
    "line_ids.tax_base_amount",
    "line_ids.balance",
    "currency_id",
    )
    def _compute_tax_summary_html(self):
        for move in self:
            move.tax_summary_html = False

            if not move.is_invoice(include_receipts=True):
                continue

            tax_lines = move.line_ids.filtered(
                lambda line: (
                    line.display_type == "tax"
                    and line.tax_line_id
                )
            )

            if not tax_lines:
                continue

            summaries = {}

            for line in tax_lines:
                tax = line.tax_line_id

                key = tax.id

                if key not in summaries:
                    summaries[key] = {
                        "name": tax.name,
                        "rate": tax.amount,
                        "base": 0.0,
                        "tax": 0.0,
                    }

                # Customer-facing invoice values should be positive.
                summaries[key]["base"] += abs(line.tax_base_amount)
                summaries[key]["tax"] += abs(line.balance)

            rows = []

            for summary in summaries.values():
                tax_name = escape(summary["name"])
                rate = f'{summary["rate"]:.2f}%'

                base_amount = escape(
                    move.currency_id.format(summary["base"])
                )

                tax_amount = escape(
                    move.currency_id.format(summary["tax"])
                )

                rows.append(
                    Markup(
                        f"""
                        <tr style="page-break-inside: avoid;">
                            <td style="
                                padding: 4px 6px;
                                border: 1px solid #444;
                            ">
                                {tax_name}
                            </td>

                            <td style="
                                text-align: right;
                                padding: 4px 6px;
                                border: 1px solid #444;
                            ">
                                {rate}
                            </td>

                            <td style="
                                text-align: right;
                                padding: 4px 6px;
                                border: 1px solid #444;
                            ">
                                {base_amount}
                            </td>

                            <td style="
                                text-align: right;
                                padding: 4px 6px;
                                border: 1px solid #444;
                            ">
                                {tax_amount}
                            </td>
                        </tr>
                        """
                    )
                )

            total_tax = sum(
                summary["tax"]
                for summary in summaries.values()
            )

            total_tax_amount = escape(
                move.currency_id.format(total_tax)
            )

            move.tax_summary_html = Markup(
                f"""
                <div class="table-responsive">

                    <table style="
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 10px;
                        page-break-inside: avoid;
                    ">

                        <thead>
                            <tr>

                                <th style="
                                    text-align: left;
                                    padding: 5px 6px;
                                    border: 1px solid #444;
                                    font-weight: 600;
                                ">
                                    Tax
                                </th>

                                <th style="
                                    text-align: right;
                                    padding: 5px 6px;
                                    border: 1px solid #444;
                                    font-weight: 600;
                                ">
                                    Rate
                                </th>

                                <th style="
                                    text-align: right;
                                    padding: 5px 6px;
                                    border: 1px solid #444;
                                    font-weight: 600;
                                ">
                                    Taxable Amount
                                </th>

                                <th style="
                                    text-align: right;
                                    padding: 5px 6px;
                                    border: 1px solid #444;
                                    font-weight: 600;
                                ">
                                    Tax Amount
                                </th>

                            </tr>
                        </thead>

                        <tbody>
                            {Markup("").join(rows)}
                        </tbody>

                        <tfoot>

                            <tr style="
                                page-break-inside: avoid;
                                font-weight: 600;
                            ">

                                <td
                                    colspan="3"
                                    style="
                                        text-align: right;
                                        padding: 5px 6px;
                                        border: 1px solid #444;
                                    "
                                >
                                    Total Tax
                                </td>

                                <td style="
                                    text-align: right;
                                    padding: 5px 6px;
                                    border: 1px solid #444;
                                ">
                                    {total_tax_amount}
                                </td>

                            </tr>

                        </tfoot>

                    </table>

                </div>
                """
            )