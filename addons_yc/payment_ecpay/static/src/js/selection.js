'use strict';
odoo.define('payment_ecpay.create_order', function (require) {
    var ajax = require('web.ajax');

    function chose_payment_type(payment_type) {
        /**
         * 同步至後端紀錄
         */
        ajax.jsonRpc('/payment/ecpay/save_payment_type', 'call', {
            payment_type: payment_type
        }).then(function () {
        });
    }

    $(document).ready(function () {
        // 預設將 selection 隱藏起來
        var selector = $('#ecpay_payment_method')
            .on('change', function () {
                chose_payment_type(this.value)
            }).hide();

        // 如果變更支付方式,則判斷是否為 ecpay以顯示下拉選單
        $('.o_payment_acquirer_select').on('click', function () {
            let select = $(this).find('input[name="pm_id"]');
            let value = select[0].dataset.provider;

            if (value === 'ecpay') {
                // 為ecpay時，顯示下拉選單並同步更新至後端紀錄
                selector.show();
                chose_payment_type(selector.val());
            } else {
                selector.hide();
            }
        });

        // 前端會根據後端的 payment method 來顯示有哪些付款方式
        if ($('input[type=radio][name=pm_id]').attr('class') !== 'hidden') {
            $('input[type=radio][name=pm_id]').change(function () {
                if (this.dataset.provider === 'ecpay') {
                    $('#ecpay_payment_method').fadeIn();
                    chose_payment_type();
                } else {
                    $('#ecpay_payment_method').fadeOut();
                }
            });
        } else {
            $('#ecpay_payment_method').fadeIn();
            chose_payment_type();
        }
    });
});