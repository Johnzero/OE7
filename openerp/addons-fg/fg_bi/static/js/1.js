

openerp.fg_bi = function(openerp)  {
    var _t = openerp.web._t,
    _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;
    openerp.web.HtmlView.include({
    on_loaded: function(data) {
        var self = this;
        if (data) {
            this.fields_order = [];
            this.fields_view = data;
            var frame = new (this.registry.get_object('frame'))(this, this.fields_view.arch);

            this.rendered = QWeb.render(this.form_template, { 'frame': frame, 'widget': this });
        }
        this.$element.html(this.rendered);
        _.each(this.widgets, function(w) {
            w.start();
        });
        this.$form_header = this.$element.find('.oe_form_header:first');
        this.$form_header.find('div.oe_form_pager button[data-pager-action]').click(function() {
            var action = $(this).data('pager-action');
            self.on_pager_action(action);
        });

        this.$form_header.find('button.oe_form_button_save').click(this.on_button_save);
        this.$form_header.find('button.oe_form_button_cancel').click(this.on_button_cancel);

        this.has_been_loaded.resolve();
        $('.secondary_menu').hide();
        $('.oe-view-manager-header').hide();
        //extend
        $('button:contains("查看数据")').click(function(){
            setTimeout("$('#refreshed').click()",1000);
            });
        $('#refreshed').click(function(){
                        $.ajax({
                        type:"GET",
                        url:'http://localhost:8069/web/static/src/data.json?+new Date()' ,
                        cache:false,
                        dataType:"json",
                        success:function(data) {
                       // Create the chart
                       window.chart = new Highcharts.StockChart({
                               chart : {
                                       renderTo : 'fuguang'
                               },
       
                               rangeSelector : {
                                       selected : 1
                               },
       
                               title : {
                                       text : 'Sales Quality Trend'
                               },
       
                               series : [{
                                       name : 'Sales Amount/Day',
                                       data : data,                                
                                       type : 'area',
                                       threshold : null,
                                       tooltip : {
                                               valueDecimals : 2
                                       },
                                       fillColor : {
                                               linearGradient : {
                                                       x1: 0, 
                                                       y1: 0, 
                                                       x2: 0, 
                                                       y2: 1
                                               },
                                               stops : [[0, Highcharts.getOptions().colors[0]], [1, 'rgba(0,0,0,0)']]
                                       }
                               }]
                       });
               }})
            }); 
    

            $(function() {
               $.getJSON('http://www.highcharts.com/samples/data/jsonp.php?filename=aapl-c.json&callback=?', function(data) {
       
                       // Create the chart
                       window.chart = new Highcharts.StockChart({
                               chart : {
                                       renderTo : 'AAPL'
                               },
       
                               rangeSelector : {
                                       selected : 1
                               },
       
                               title : {
                                       text : 'AAPL Stock Price'
                               },
       
                               series : [{
                                       name : 'AAPL Stock Price',
                                       data : data,
                                       type : 'area',
                                       threshold : null,
                                       tooltip : {
                                               valueDecimals : 2
                                       },
                                       fillColor : {
                                               linearGradient : {
                                                       x1: 0, 
                                                       y1: 0, 
                                                       x2: 0, 
                                                       y2: 1
                                               },
                                               stops : [[0, Highcharts.getOptions().colors[0]], [1, 'rgba(0,0,0,0)']]
                                       }
                               }]
                       });
               });
       });
            
            

           
    },
        });
    }
    