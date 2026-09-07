{
    "name": "Invoice Tax Summary",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Display detailed tax summaries on customer invoices",
    "description": """
Invoice Tax Summary

Adds a detailed tax summary to customer invoices,
including individual tax components, tax rates,
taxable amounts and tax amounts.

The tax summary is available directly on the invoice
and can also be included in the printed invoice.

Designed for businesses using GST, VAT and other
tax-based invoicing systems.
""",

    "author": "Madcodres Technologies LLP",
    "website": "https://madcodres.com",
    "support": "info@madcodres.com",
    "license": "OPL-1",

    "depends": [
        "account",
    ],

    "data": [
        "views/account_move_views.xml",
        "views/report_invoice_views.xml",
    ],

    "images": [
        "static/description/tax_summary_report1.png",
        "static/description/tax_summary_report2.png",
        "static/description/tax_summary_print.png",
        "static/description/tax_summary_invoice_tab.png",
        "static/description/tax_summary_invoice_bottom.png",
    ],

    "application": True,
    "installable": True,
}