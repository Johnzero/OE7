/*############################################################################
#    Web PDF Report Preview & Print
#    Copyright 2012 wangbuke <wangbuke@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################*/

openerp.fg_report = function(instance) {

    // TODO: FIX ERROR
    // TypeError: this.get_action_manager(...) is undefined on Firefox
    // TypeError: Cannot call method 'get_title' of undefined on Chrome / IE

    
    instance.web.ActionManager = instance.web.ActionManager.extend({
        init: function (parent, action) {
            this._super();
            //$.getscript("/fg_report/static/src/js/LodopFuncs.js");
            $("body").append('<script language="javascript" src="/fg_report/static/src/js/LodopFuncs.js"></script>');
            $("body").append('<object id="LODOP_OB" classid="clsid:2105C259-1E0C-4534-8141-A753534CB4CA" width=0 height=0><embed id="LODOP_EM" type="application/x-print-lodop" width=0 height=0 pluginspage="/fg_report/static/src/js/install_lodop.exe"></embed></object>');
            console.log(document.getElementsByTagName('HEAD')[0]);
        },
    
        ir_actions_report_xml: function(action, options) {
            var self = this;
            instance.web.blockUI();
            return instance.web.pyeval.eval_domains_and_contexts({
                contexts: [action.context],
                domains: []
            }).then(function(res) {
                action = _.clone(action);
                action.context = res.context;
                var os = navigator.platform || "Unknown OS";
                linux = os.indexOf("Linux") > -1;
                if(!linux) {
                    
                    self.rpc("/web/report/pdf", {
                        action: JSON.stringify(action),
                        token: new Date().getTime()
                    }).done(function(result) {
                        instance.web.unblockUI();
                        self.dialog_stop();
                        LODOP = getLodop(document.getElementById('LODOP'),document.getElementById('LODOP_EM'));
                        LODOP.ADD_PRINT_TABLE("0mm","0mm","220mm", "92mm", $(result.report)[5].innerHTML);
                        LODOP.PREVIEW();

                    });
                    
                }
                else {
                    self.rpc("/web/report/pdf_token", {
                        action: JSON.stringify(action),
                        token: new Date().getTime()
                    }).done(function(result) {
                        instance.web.unblockUI();
                        self.dialog_stop();
                        //openwindow = window.open('/web/report/pdf?pdf_file_token=' + result.pdf_file_token + '&session_id=' + self.session.session_id, 'report', '');

                    });
                    var c = instance.webclient.crashmanager;
                    return $.Deferred(function (d) {
                        self.session.get_file({
                            url: '/web/report',
                            data: {action: JSON.stringify(action)},
                            complete: instance.web.unblockUI,
                            success: function(){
                                if (!self.dialog) {
                                    options.on_close();
                                }
                                self.dialog_stop();
                                d.resolve();
                            },
                            error: function () {
                                c.rpc_error.apply(c, arguments);
                                d.reject();
                            }
                        })
                    });
                }
            });
        },
    });


};


