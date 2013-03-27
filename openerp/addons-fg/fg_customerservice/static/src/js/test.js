openerp.fg_customerservice = function(session) {
    var QWeb = session.web.qweb;
    _t = session.web._t;
    session.web.Sidebar.include({
        add_toolbar: function(toolbar) {
        var self = this;
        _.each([['print', _t("Reports")], ['action', _t("Actions")], ['relate', _t("Links")]], function(type) {
            var items = toolbar[type[0]];
            if (items.length) {
                for (var i = 0; i < items.length; i++) {
                    items[i] = {
                        label: items[i]['name'],
                        action: items[i],
                        classname: 'oe_sidebar_' + type[0]
                    }
                }
                self.add_section(type[1], type[0]);
                self.add_items(type[0], items);
            }
        });
    //extend
    if  ($('th[data-id="receive_num"]').length){
        $('.sidebar-content')[0].innerHTML +="<img style='width:180px' src='/web/static/src/img/taobao.jpg'></img>"
    }
        
    },
        })
}
