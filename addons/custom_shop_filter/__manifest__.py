{
    "name": "Custom Shop Filter",
    "version": "18.0.0.1",
    "author": "varoESP",
    "website": "https://github.com/VaroESP/Custom_Odoo_Modules",
    "category": "Education",
    "summary": "Add filter and slide bar in shop page",
    "depends": ["base", "website_sale"],
    "data": [
        "views/product_attribute_views.xml",
        "views/product_attribute_value_views.xml",
        "views/website_templates.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "custom_shop_filter/static/src/js/website_range_option.js",
        ],
    },
    "installable": True,
    "application": False,
    "languages": ["es"],
    "license": "LGPL-3"
}
