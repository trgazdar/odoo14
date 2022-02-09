odoo.define('logistic_ecpay.client_shipping_select', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var CustomPageDemo = AbstractAction.extend({
        template: 'shipping_template',
        events: { 'click .o_print_cvs_button': '_onSubmitClick' },
        init: function (parent, node) {
            this._super(parent, node);
            this.ecpay = {};
            this.ecpay.ecpay_unimart = true;
            this.ecpay.ecpay_fami = true;
        },
        _onSubmitClick: function (e) {
            e.stopPropagation();
            alert('Submit clicked!');
        }
    });

    core.action_registry.add('logistic_ecpay.client_shipping_select', CustomPageDemo);

    return CustomPageDemo;

});