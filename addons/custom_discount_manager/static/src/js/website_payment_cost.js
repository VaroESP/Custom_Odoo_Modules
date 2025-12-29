/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.PaymentDiscount = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'change input[name="o_payment_radio"]': '_onPaymentMethodChange',
    },

    async start() {
        const res = await this._super.apply(this, arguments);
        const selected = this.el.querySelector('input[name="o_payment_radio"]:checked');

        if (!selected) {
            try {
                const data = await rpc('/shop/payment/update_discount');
                if (data) {
                    const $cartTotal = $('#cart_total');
                    if ($cartTotal.length) {
                        $cartTotal.replaceWith(data);
                    }
                    $.get(window.location.href, function (data) {
                        var nuevoHtml = $(data).find('#amount_total_summary').html();
                        if (nuevoHtml) {
                            $('#amount_total_summary').html(nuevoHtml);
                        }
                    });
                }
            } catch (error) {
                console.warn("Aviso: No se pudo resetear el descuento inicial.");
            }
        }
        return res;
    },

    async _onPaymentMethodChange(ev) {
        const $input = $(ev.currentTarget);
        const paymentMethodId = $input.data('payment-option-id') || $input.data('payment-method-id');

        if (!paymentMethodId) {
            return;
        }
        try {
            const data = await rpc('/shop/payment/update_discount', {
                'payment_method_id': paymentMethodId,
            });

            if (data) {
                const $cartTotal = $('#cart_total');
                if ($cartTotal.length) {
                    $cartTotal.replaceWith(data);
                }
                $.get(window.location.href, function (data) {
                    var nuevoHtml = $(data).find('#amount_total_summary').html();
                    if (nuevoHtml) {
                        $('#amount_total_summary').html(nuevoHtml);
                    }
                });
            }
        } catch (error) {
            console.error("Error actualizando descuento:", error);
        }
    },
});