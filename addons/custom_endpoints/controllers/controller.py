from odoo import http
from odoo.http import request, Response
import json
import logging
_logger = logging.getLogger(__name__)

class ControllerProductApi(http.Controller):

    @http.route("/api/update-product", auth="public", type="http", methods=["POST"], csrf=False)
    def update_product_api(self, **kwargs):
        try:
            raw_data = request.httprequest.get_data()
            if not raw_data:
                return Response(
                    json.dumps({"error": "Bad Request", "message": "No data provided", "code": 400}),
                    status=400, content_type="application/json"
                )

            try:
                data = json.loads(raw_data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return Response(
                    json.dumps({"error": "Bad Request", "message": "Invalid JSON format", "code": 400}),
                    status=400, content_type="application/json"
                )

            if data.get("token") != "asdfghjklqwertyuiop":
                return Response(
                    json.dumps({
                        "error": "Unauthorized",
                        "message": "Token inválido",
                        "code": 401
                    }),
                    status=401,
                    content_type="application/json"
                )

            type_mapping = {
                "product": "consu",
                "service": "service",
                "consu": "consu",
                "storable": "consu",
                "consumible": "consu",
                "combo": "combo",
            }
            product_type = type_mapping.get(data.get("type"), "consu")

            default_code = data.get("default_code")
            if not default_code:
                return Response(
                    json.dumps({"error": "Bad Request", "message": "default_code is required", "code": 400}),
                    status=400, content_type="application/json"
                )

            product = request.env["product.template"].sudo().search([("default_code", "=", default_code)], limit=1)

            product_vals = {
                "name": data.get("name", "Producto sin nombre"),
                "type": product_type,
                "description_sale": data.get("description_sale", ""),
                "list_price": float(data.get("list_price", 0.0)),
                "standard_price": float(data.get("standard_price", 0.0)),
                "default_code": default_code,
            }

            if product:
                product.write(product_vals)
                response_data = {
                    "status": "updated",
                    "product_id": product.id,
                    "message": f"Product {product.name} updated",
                }
            else:
                new_product = request.env["product.template"].sudo().create(product_vals)
                response_data = {
                    "status": "created",
                    "product_id": new_product.id,
                    "message": f"Product {new_product.name} created",
                }

            return Response(
                json.dumps(response_data),
                status=200,
                content_type="application/json"
            )

        except Exception as e:
            _logger.error(f"Error in update_product_api: {str(e)}")
            return Response(
                json.dumps({
                    "error": "Internal Server Error",
                    "message": str(e),
                    "code": 500
                }),
                status=500,
                content_type="application/json"
            )