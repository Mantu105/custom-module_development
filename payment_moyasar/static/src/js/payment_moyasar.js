/** @odoo-module **/

import paymentForm from '@payment/js/payment_form';
import payment_mayosar from '@payment_moyasar/js/moyasar_min';


function isValidName(name) {
    return /^[a-zA-Z\s]{2,}$/.test(name);
}

function isValidCardNumber(number) {
    const sanitized = number.replace(/\s+/g, '');
    return /^[0-9]{16}$/.test(sanitized);
}

function isValidExpiry(expiry) {
    if (!/^\d{2}\/\d{2}$/.test(expiry)) return false;
    const [month, year] = expiry.split('/').map(x => parseInt(x, 10));
    if (month < 1 || month > 12) return false;

    const now = new Date();
    const fullYear = 2000 + year;
    const expDate = new Date(fullYear, month - 1, 1);
    return expDate >= new Date(now.getFullYear(), now.getMonth(), 1);
}

function isValidCVC(cvc) {
    return /^[0-9]{3,4}$/.test(cvc);
}



paymentForm.include({

    setupValidation() {
        const nameInput = document.getElementById('name');
        const cardInput = document.getElementById('card-number');
        const expiryInput = document.getElementById('expiry');
        const cvcInput = document.getElementById('cvc');

        if (!nameInput || !cardInput || !expiryInput || !cvcInput) return;

        const validateAll = () => {
            const validName = isValidName(nameInput.value);
            const validCard = isValidCardNumber(cardInput.value.replace(/\s+/g, ''));
            const validExpiry = isValidExpiry(expiryInput.value);
            const validCVC = isValidCVC(cvcInput.value);

            nameInput.style.borderColor = validName ? 'green' : 'red';
            cardInput.style.borderColor = validCard ? 'green' : 'red';
            expiryInput.style.borderColor = validExpiry ? 'green' : 'red';
            cvcInput.style.borderColor = validCVC ? 'green' : 'red';

            if (validName && validCard && validExpiry && validCVC) {
                this._enableButton(false);
            } else {
                this._disableButton(false);
            }
        };

        nameInput.addEventListener('input', validateAll);
        cardInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            e.target.value = value.replace(/(.{4})/g, '$1 ').trim();
            validateAll();
        });
        expiryInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 2) value = value.slice(0,2) + '/' + value.slice(2,4);
            e.target.value = value;
            validateAll();
        });
        cvcInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');
            validateAll();
        });

        validateAll();
    },

    async start() {
        this.paymentContext = {};
        Object.assign(this.paymentContext, this.el.dataset);

        await this._super(...arguments);

        const checkedRadio = document.querySelector('input[name="o_payment_radio"]:checked');
        if (checkedRadio) {
            await this._expandInlineForm(checkedRadio);
            this._enableButton(false);
        } else {
            this._setPaymentFlow();
        }
        const providerCode = document.querySelector('input[name="o_payment_radio"]:checked')?.dataset.providerCode;
        if (providerCode == 'moyasar'){
            this._disableButton(false);
        }

        this.$('[data-bs-toggle="tooltip"]').tooltip();
    },

    /**
     * Prepare the inline form of Demo for direct payment.
     *
     * @override method from @payment/js/payment_form
     * @private
     * @param {number} providerId - The id of the selected payment option's provider.
     * @param {string} providerCode - The code of the selected payment option's provider.
     * @param {number} paymentOptionId - The id of the selected payment option
     * @param {string} paymentMethodCode - The code of the selected payment method, if any.
     * @param {string} flow - The online payment flow of the selected payment option.
     * @return {void}
     */
    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'moyasar') {
            this._super(...arguments);
            return;
        } else if (flow === 'token') {
            return;
        }
        this.setupValidation();
        this._setPaymentFlow('direct');
    },

    /**
     * Simulate a feedback from a payment provider and redirect the customer to the status page.
     *
     * @override method from payment.payment_form
     * @private
     * @param {string} providerCode - The code of the selected payment option's provider.
     * @param {number} paymentOptionId - The id of the selected payment option.
     * @param {string} paymentMethodCode - The code of the selected payment method, if any.
     * @param {object} processingValues - The processing values of the transaction.
     * @return {void}
     */
    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'moyasar') {
            this._super(...arguments);
            return;
        }
        payment_mayosar.processDemoPayment(processingValues);
    },



    
});
