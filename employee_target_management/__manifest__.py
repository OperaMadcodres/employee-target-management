{
    "name":"Employee Target Management",
    "version":"19.0.1.0.0",
    "category":"Sales/Sales",
    "summary":"Manage employee targets and performance",
    "description":"""
        Employee Target Management

        Manage employee targets, assignments,
        target periods and target progress.
    """,
    "author": "Madcodres Technologies LLP",
    "website": "https://madcodres.com",
    "license": 'OPL-1',
    "depends":[
        "base",
        "hr",
        'sale',
        'account',
        'web',
    ],
    "data":[
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/employee_target_rules.xml',
        
        "views/target_type_views.xml",
        "views/target_period_views.xml",
        "views/employee_target_views.xml",
        'views/dashboard_views.xml',
        'views/menus.xml',

        'data/cron.xml',
    ],
    "application": True,
    "installable": True,
    "images": [
    "images/employee_target_dashboard_screenshot.jpeg",
    "images/employee_target_form.jpeg",
    "images/employee_target_list.jpeg",
    "images/employee_target_types.jpeg",
    "images/employee_target_workflow.png",
    ],

    'assets': {
    'web.assets_backend': [
        '/web/static/lib/Chart/Chart.js',

        'employee_target_management/static/src/js/employee_target_dashboard.js',
        'employee_target_management/static/src/xml/employee_target_dashboard.xml',
        'employee_target_management/static/src/css/employee_target_dashboard.css',
    ],
},
}