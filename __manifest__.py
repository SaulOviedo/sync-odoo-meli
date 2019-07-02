# -*- coding: utf-8 -*-
{
    'name': "MercadoLibre Sync",

    'summary': """ Envia tu inventario a Mercadolibre. """,

    'description': """
        Instrucciones para su Uso:
	    - Habilite 'Variantes del producto' en Ventas > Configuracion > Ajustes
	    - Seleccione el país e inicie Sesión en Configuracion > Compañias > {suCompañia} > Mercadolibre
     	    Ahora puede usar el Modulo Sync y Enviar su inventario a mercadolibre.
    """,

    'author': "ChileDev",
    'website': "http://chiledev.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','stock','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
	'data/automatic.xml',
        'views/main.xml',
	'views/company_view.xml',
        'views/product.xml',
        'views/orders.xml',
	'views/questions.xml',
        'views/buyers.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
