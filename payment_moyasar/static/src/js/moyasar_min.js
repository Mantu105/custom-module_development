/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

export default {
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    /**
     * Process a payment through Moyasar API and redirect based on status
     *
     * @param {object} processingValues - Optional additional values
     */
    async processDemoPayment(processingValues = {}) {
        try {
            const name = document.getElementById('name')?.value;
            let cardNumber = document.getElementById('card-number')?.value;
            cardNumber = cardNumber ? cardNumber.replace(/\s+/g, '') : '';
            const expiry = document.getElementById('expiry')?.value;
            const [month, year] = expiry.split('/').map(x => parseInt(x.trim(), 10));
            const cvc = document.getElementById('cvc')?.value;

            const amount = parseInt(processingValues.amount);
            const res_currency = await rpc("/web/dataset/call_kw", {
                model: "res.currency",
                method: "read",
                args: [[processingValues.currency_id], ["name", "symbol"]],
                kwargs: {},
            });
            const currency = res_currency[0].name;
            const callback_url = window.location.origin + "/get/moyasar/order";

            const given_id = this.generateUUID();
            const payload = {
                given_id,
                amount,
                currency,
                callback_url,
                source: {
                    type: "creditcard",
                    name,
                    number: cardNumber,
                    month,
                    year,
                    cvc,
                    statement_descriptor: "Century Store",
                    "3ds": true,
                    manual: false,
                    save_card: false,
                }
            };

            const provider_details = await rpc("/web/dataset/call_kw", {
                model: "payment.provider",
                method: "read",
                args: [[processingValues.provider_id], ["moyasar_public_key", "moyasar_secret_key"]],
                kwargs: {},
            });

            const username = provider_details[0].moyasar_public_key;
            const password = provider_details[0].moyasar_secret_key;
            const response = await fetch("https://api.moyasar.com/v1/payments", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Basic " + btoa(username + ":" + password)
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            if (!response.ok) {
                if (data.errors == null){
                    const errorText = data?.message;
                    alert(_t("Invalid Data: ") + errorText);
                }
                else{
                    const errors = data?.errors;
                    const allErrors = Object.entries(errors).flatMap(([key, messages]) => {
                        if (Array.isArray(messages)) {
                            return messages.map(msg => `Invalid Data: ${msg}`);
                        }
                        return [`Invalid Data: ${messages}`];
                    });
                    alert(allErrors.join('\n'));
                }
                window.location.reload();
            }
            
            if (data.status === "initiated") {
                window.location.href = data.source.transaction_url;
            }

        } catch (err) {
            alert("Payment failed.", err);
        }
    },
};