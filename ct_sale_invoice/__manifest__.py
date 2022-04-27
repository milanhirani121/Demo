# -*- coding: utf-8 -*-

{
    'name': 'ct sale invoice',
    'version': '12.0.1.0.1',
    'category': 'Custom',
    'description': """
        Sales & invoice
        
    """,
    'author': '',
    'license': 'OPL-1',
    'website': '',
    'depends': ['sale','account','qr_generator'],
    'data': ['views/work_order_view.xml',
             'views/sale_quatation_form.xml',
             'views/wt_account_report.xml',
             'views/ct_invoice _report.xml',
             'views/res_company.xml'
    ],
    'qweb': [],
    'demo': [],
    'application': False,
    'installable': True,
}
