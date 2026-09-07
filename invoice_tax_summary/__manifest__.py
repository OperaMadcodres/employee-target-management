{
    "name": "Invoice Tax Summary",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Display detailed tax summaries on customer invoices",
    "description": """
Invoice Tax Summary

Adds a detailed tax summary to customer invoices,
including tax groups, taxable amounts and tax amounts.

Designed for businesses using GST, VAT and other tax systems.
""",
    "author": "Madcodres Technologies LLP",
    "website": "https://madcodres.com",
    "license": "OPL-1",

    "depends": [
        "account",
    ],

    "data": [   
        "views/account_move_views.xml",
        "views/report_invoice_views.xml",
    ],

    "installable": True,
    "application": True,
}