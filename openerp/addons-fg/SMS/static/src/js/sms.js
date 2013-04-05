openerp.SMS = function (session) { 

    session.web.ComposeFetionTopButton = session.web.Widget.extend({

        template:'sms.ComposeFetionTopButton',

        start: function () {
            this._super();
            $('#fetion').on('click', this.on_compose_message );
        },

        on_compose_message: function (event) {
            event.stopPropagation();
            var action = {
                type: 'ir.actions.act_window',
                res_model: 'fetion',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {},
            };
            session.client.action_manager.do_action(action);
        },

    });

    session.web.UserMenu.include({
        do_update: function(){
            var self = this;
            this._super.apply(this, arguments);
            this.update_promise.then(function() {
                var fetion_button = new session.web.ComposeFetionTopButton();
                fetion_button.appendTo(session.webclient.$el.find('.oe_systray'));
            });
        },
    });

}
