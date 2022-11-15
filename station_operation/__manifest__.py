# -*- coding: utf-8 -*-
{
    'name': "station_operation",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Station Opertion limited",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/views_product_inherit.xml',
        'views/views_tanks.xml',
        'views/views_station_master_data.xml',
        'views/views_pivot_reports.xml',
        'data/mail_template_data2.xml',
        'security/station_security.xml',
    ],
    'external_dependencies': {
        'python': ['pyodbc'],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
