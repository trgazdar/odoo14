odoo.define('logistic_ecpay.logistic_ecpay_shopping_stage', function (require) {
    'use strict';

    // 建立環境-變數
    require('web.dom_ready');
    let ajax = require('web.ajax');
    let checked_label;
    let check_name = false, check_mobile = false, check_address = false, check_store = false;
    let func = {
            ecpay_unimart: () => {  // 7-11
                operator
                    .display('#ecpay-card')
                    .display_store()
                    .clear_store_address();

                submit_button_validate();
                $('#shipping_store').val('ecpay');
                return 'Run function "ecpay_unimart"';
            },
            ecpay_fami: () => {     // 全家
                operator
                    .display('#ecpay-card')
                    .display_store()
                    .clear_store_address();

                submit_button_validate();
                $('#shipping_store').val('ezship');
                return 'Run function "ecpay_fami"';
            },
            ecpay_hilife: () => {   // 萊爾富
                operator
                    .display('#ecpay-card')
                    .display_store()
                    .clear_store_address();

                submit_button_validate();
                $('#shipping_store').val('ezship');
                return 'Run function "ecpay_hilife"';
            },
            ecpay_ecan: () => {
                operator
                    .display('#ecpay-card')
                    .display_home()
                    .clear_store_address();

                submit_button_validate();
                $('#shipping_store').val('home');
                return 'Run function "ecpay_ecan"';
            },
            ecpay_tcat: () => {
                operator
                    .display('#ecpay-card')
                    .display_home()
                    .clear_store_address();

                submit_button_validate();
                $('#shipping_store').val('home');
                return 'Run function "ecpay_tcat"';
            },
            not_ecpay: () => {
                operator
                    .display('#ecpay-card', false)
                    .clear_store_address();
                $('#shipping_store').val('');
                submit_button.removeClass('d-none');
                return 'Not Ecpay';
            }
        };

    let operator = {
        display: function (selector, show = true) {
            $(selector)[show === true ? 'removeClass' : 'addClass']('d-none');

            return this;
        },
        display_store: function (show = true) {
            $('#ecpay_loistic_receiver_address').addClass('d-none');
            $('#ecpay_logistic_store_info').removeClass('d-none');

            return this;
        },
        display_home: function (show = true) {
            $('#ecpay_loistic_receiver_address').removeClass('d-none');
            $('#ecpay_logistic_store_info').addClass('d-none');

            return this;
        },
        clear_store_address: function () {
            // 清除超商及地址
            this.display('.ecpaylogistic-warning');
            $('#CVSStoreID').val('');
            $('#CVSAddress').val('');
            $('#ReceiverAddress').val('');
            check_address = false;
            check_store = false;

            return this;
        }
    }

    operator
        // 收件人姓名警告
        .display('#warning-ReceiverName', false)
        // 收件人手機警告
        .display('#warning-ReceiverCellPhone', false)
        // 收件人地址警告
        .display('#warning-ReceiverAddress', false);

    // 抓取原生下一步按鈕
    let submit_button = $('#o_payment_form_pay').prop('disabled', true);

    // 檢查哪一種物流被選取
    let check_delivery = async (selector) => {
        let _id = selector
            ? $(selector).find('input')[0].value
            : document.querySelector('input[name="delivery_type"]:checked').value;

        let response = await ajax.jsonRpc('/shipping/get_delivery_method_name', 'call', {id: _id});
        if (response.service === 'ecpay' && func[response.method]) {
            func[response.method]();
        } else {
            func['not_ecpay']();
        }
        checked_label = response;
    }

    // 傳送資料到後端
    let send_shipping_info = async () => {
        let shipping_info_package = {
            shipping_store: $('#shipping_store').val(),
            cvs_id: $('#cvs_id').val(),
            home_zip_code: $('#twzipcode').twzipcode('get', 'zipcode')[0],
            home_address: $('#twzipcode').twzipcode('get', 'county') + $('#twzipcode').twzipcode('get', 'district') + $('#ReceiverAddress').val(),
            receiver_name: $('#ReceiverName').val(),
            receiver_mobile: $('#ReceiverCellPhone').val(),
        }
        if (shipping_info_package != null) {
            await ajax.jsonRpc('/shipping/save_shipping_info', 'call', {
                shipping_info_package: shipping_info_package,
            }).then(function (res) {
                console.log(res);
            }).catch(res => {
                console.error('Server Error!', res);
            });
        }
    }

    let check_warning = () => {
        console.log('check_name', check_name);
        console.log('check_mobile', check_mobile);
        console.log('check_address', check_address);
        $('#warning-ReceiverName')[check_name ? 'addClass' : 'removeClass']('d-none');
        $('#warning-ReceiverCellPhone')[check_mobile ? 'addClass' : 'removeClass']('d-none');
        $('#warning-ReceiverAddress')[check_address ? 'addClass' : 'removeClass']('d-none');
    }

    let submit_button_validate = () => {
        let method = checked_label ? checked_label['method'] : '';
        let btn_display = bool => {
            if (bool && submit_button.hasClass('d-none')) {
                submit_button.removeClass('d-none');
            } else if (!bool && !submit_button.hasClass('d-none')) {
                submit_button.addClass('d-none');
            }
        };
        if ($.inArray(method, ['ecpay_unimart', 'ecpay_fami', 'ecpay_hilife']) !== -1) {
            btn_display(check_name && check_mobile && check_store);
        } else {
            btn_display(check_name && check_mobile && check_address)
        }
        check_warning();
    }

    let check_name_length = (name) => {
        let l = name.length;
        let blen = 0;
        for (let i = 0; i < l; i++) {
            if ((name.charCodeAt(i) & 0xff00) != 0) {
                blen++;
            }
            blen++;
        }
        return blen;
    }

    // 觸發區
    if ($("#delivery_method").length) {
        operator.clear_store_address();
        check_delivery();
        submit_button_validate(); // 先將付款按鈕 disable
    }

    // 1. 字元限制為為 4~10 字元(中文 2~5 個字, 英文 4~10 個字)
    // 2. 不可有符號^ ' ` ! ＠ # % & * + \ " < > | _ [ ]
    // 3. 不可有空白 , 及，若帶有空白, 及，系統自動去除。
    // 檢查姓名是否輸入
    $('#ReceiverName').on('input', () => {
        let is_name = $('#ReceiverName').val();
        let format = /[ !@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;
        let format_number = /[0-9]/;
        console.log(check_name_length(is_name), format.test(is_name), format_number.test(is_name))
        if (is_name && check_name_length(is_name) >= 4 && check_name_length(is_name) <= 10 &&
            (format.test(is_name) === false) && (format_number.test(is_name) === false)) {
            $('#div-ReceiverName').removeClass("has-error");
            check_name = true;
        } else {
            $('#div-ReceiverName').addClass("has-error");
            check_name = false;
        }
        submit_button_validate();
    });

    // 檢查是否輸入手機號碼
    $('#ReceiverCellPhone').on('input', () => {
        let re = /^[09]{2}[0-9]{8}$/;
        let is_mobile = re.test($('#ReceiverCellPhone').val());
        if (is_mobile) {
            $('#div-ReceiverCellPhone').removeClass("has-error");
            check_mobile = true;
        } else {
            $('#div-ReceiverCellPhone').addClass("has-error");
            check_mobile = false;
        }
        submit_button_validate();
    });

    // 檢查是否輸入地址
    $('#ReceiverAddress').on('input', () => {
        let is_address = $('#ReceiverAddress').val();
        let zipcode = $('#twzipcode').twzipcode('get', 'zipcode');
        if (is_address && is_address.length >= 6 && is_address.length <= 60 && (zipcode != false)) {
            $('#div-ReceiverAddress').removeClass("has-error");
            check_address = true;
        } else {
            $('#div-ReceiverAddress').addClass("has-error");
            check_address = false;
        }
        submit_button_validate();
    });

    // 當選擇 delivery method 時, 去執行 function
    $('#delivery_method li').on('click', function () {
        check_delivery(this);
    });

    // 當選擇 delivery method 時, 去執行 function
    $('#cvs_store').on('click', function () {
        let show_cvs_url = '/shipping/map/';
        let part_url = (checked_label.method === 'ecpay_unimart') ? 'UNIMART' : 'EZSHIP';
        show_cvs_url += part_url;

        // 開啟一個新視窗
        let win = window.open(show_cvs_url, 'CVS map', 'width=1024,height=600,status=no,scrollbars=yes,toolbar=no,location=no,menubar=no');
        // 偵測是否關掉視窗, 關掉後會發 ajax 給 server 請求 store info
        let timer = setInterval(function () {
            if (win.closed) {
                clearInterval(timer);
                ajax.jsonRpc('/shipping/update_carrier', 'call', {})
                    .then(function (data) {
                        if (data.CVSStoreID || data.CVSStoreName || data.CVSAddress) {
                            $('#CVSStoreID').val(`${data.CVSStoreID} / ${data.CVSStoreName}`);
                            $('#CVSAddress').val(data.CVSAddress);
                            $('#shipping_store').val(data.CVSStoreName);
                            $('#cvs_id').val(data.CVSStoreID);
                            operator.display('.ecpaylogistic-warning', false);
                            $('.ecpaylogistic-warning').hide();
                            check_store = true;
                        } else {
                            operator.display('.ecpaylogistic-warning');
                            check_store = false;
                        }
                    });
            }
        }, 1000);
    });

    // 按下驗證後，傳送當前訊息到 sale.order
    if (submit_button.length) {
        submit_button.on('click', function() {
            send_shipping_info().then(() => {
                console.log('Send shipping info done.');
            });
        });
    }

    // is_ecpay 定義在 logistic_ecpay_templates.xml  id="logistic_ecpay_shopping_stage" 的視圖裡
    if (is_ecpay === true) {
        operator.display('#ecpay-card');
        func[func[method] ? method : 'not_ecpay']();
    }
});