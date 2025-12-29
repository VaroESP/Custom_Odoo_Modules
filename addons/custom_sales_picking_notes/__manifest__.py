{
    "name": "Custom Sales and Picking notes",
    "version": "18.0.0.1",
    "author": "varoESP",
    "website": "https://github.com/VaroESP/Custom_Odoo_Modules",
    "category": "Education",
    "summary": "Add a text field called 'notes' to sale.order and stock.picking",
    "depends": ['base', 'sale', 'stock', 'sale_stock'],
    "data": [
        'views/website_sale_order_views.xml',
        'views/stock_picking_views.xml'
    ],
    "installable": True,
    "application": False,
    "languages": ["es"],
    "license": "LGPL-3",
}
