{
    "name": "Custom Discount Manager",
    "version": "18.0.0.1",
    "author": "varoESP",
    "website": "https://github.com/VaroESP/Custom_Odoo_Modules",
    "category": "Education",
    "summary": "Add discount to chosee a payment methods",
    "depends": ['base', 'payment', 'website_sale'],
    "data": [
        'views/payment_provider_views.xml',
        'views/payment_form_templates.xml'
    ],
    "assets": {
        "web.assets_frontend": [
            "custom_discount_manager/static/src/js/website_payment_cost.js",
        ],
    },
    "installable": True,
    "application": False,
    "languages": ["es"],
    "license": "LGPL-3",
}
