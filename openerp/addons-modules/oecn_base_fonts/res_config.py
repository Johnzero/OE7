# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from reportlab.lib.styles import ParagraphStyle
import openerp.report.render.rml2pdf.customfonts as cfonts
from openerp import SUPERUSER_ID
from report import report_sxw,interface
from lxml import etree
import base64
import pooler
import re
import tools
from copy import deepcopy

RMLS = ['rml_header','rml_header2','rml_header3']
OE_FONTS = ['Helvetica','DejaVuSans','Times','Times-Roman','Courier']

class font_configuration(osv.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'base_font' : fields.char('Font Url'),
        'cjk_wrap': fields.boolean('CJK Wrap', help="CJK warp"),
    }
    
    _defaults = {
        'base_font': 'C:\Windows\Fonts\msyhbd.ttf',
        'cjk_wrap': True,
    }
            
    def get_default_base_font(self, cr, uid, ids, context=None):
        config_parameter_obj = self.pool.get("ir.config_parameter")
        base_font = config_parameter_obj.get_param(cr, uid, "font_url", context=context)
        #base_font_name = config_parameter_obj.get_param(cr, uid, "base_font_name", context=context)
        cjk_wrap = config_parameter_obj.get_param(cr, uid, "cjk_wrap", context=context)
        return {'base_font' : base_font,'cjk_wrap' : cjk_wrap}
    
    def set_base_font(self, cr, uid, ids, context=None):
        config_parameter_obj = self.pool.get("ir.config_parameter")
        company_obj = self.pool.get("res.company")
        company_ids = company_obj.search(cr, uid, [])
        for record in self.browse(cr, uid, ids, context=context):
            config_parameter_obj.set_param(cr, uid, "font_url", record.base_font or '', context=context)
            config_parameter_obj.set_param(cr, uid, "cjk_wrap", record.cjk_wrap or '', context=context)
            
def create_single_pdf(self, cr, uid, ids, data, report_xml, context=None):
    if not context:
        context={}
    logo = None
    context = context.copy()
    title = report_xml.name
    rml = report_xml.report_rml_content
    # if no rml file is found
    if not rml:
        return False
    rml_parser = self.parser(cr, uid, self.name2, context=context)
    objs = self.getObjects(cr, uid, ids, context)
    rml_parser.set_context(objs, data, ids, report_xml.report_type)
    processed_rml = etree.XML(rml)
    if report_xml.header:
        rml_parser._add_header(processed_rml, self.header)
    processed_rml = self.preprocess_rml(processed_rml,report_xml.report_type)
    if rml_parser.logo:
        logo = base64.decodestring(rml_parser.logo)
    create_doc = self.generators[report_xml.report_type]
    # change the fontname 
    install_ids = pooler.get_pool(cr.dbname).get('ir.module.module').search(cr, uid, [('name','=','oecn_base_fonts'),('state','=','installed')])
    originCustomTTFonts = deepcopy(cfonts.CustomTTFonts)
    if install_ids:
        config_parameter_obj = pooler.get_pool(cr.dbname).get("ir.config_parameter")
        base_font = config_parameter_obj.get_param(cr, uid, "font_url")
        #base_font_name = config_parameter_obj.get_param(cr, uid, "base_font_name")
        cjk_wrap = config_parameter_obj.get_param(cr, uid, "cjk_wrap")
        fonts_map = []
        if base_font:
            for font in OE_FONTS:
                fonts_map += [(font, 'myFont', base_font, 'all')]
        cfonts.CustomTTFonts = fonts_map
        ParagraphStyle.defaults['wordWrap'] = cjk_wrap and 'CJK' or ''
        for p in processed_rml.findall('.//setFont'):
            p.set('name','myFont')
        for p in processed_rml.findall('.//*[@fontName]'):
            p.set('fontName','myFont')
    
    # change the fontname 
    pdf = create_doc(etree.tostring(processed_rml),rml_parser.localcontext,logo,title.encode('utf8'))
    # use the origin one
    cfonts.CustomTTFonts = originCustomTTFonts
    return pdf, report_xml.report_type

# xsl:xml report
def create(self, cr, uid, ids, datas, context):
    xml = self.create_xml(cr, uid, ids, datas, context)
    xml = tools.ustr(xml).encode('utf8')
    report_type = datas.get('report_type', 'pdf')
    if report_type == 'raw':
        return xml, report_type
    rml = self.create_rml(cr, xml, uid, context)
    pool = pooler.get_pool(cr.dbname)
    ir_actions_report_xml_obj = pool.get('ir.actions.report.xml')
    report_xml_ids = ir_actions_report_xml_obj.search(cr, uid, [('report_name', '=', self.name[7:])], context=context)
    self.title = report_xml_ids and ir_actions_report_xml_obj.browse(cr,uid,report_xml_ids)[0].name or 'OpenERP Report'
    create_doc = self.generators[report_type]
    # change the fontname
    install_ids = pool.get('ir.module.module').search(cr, uid, [('name','=','oecn_base_fonts'),('state','=','installed')])
    originCustomTTFonts = deepcopy(cfonts.CustomTTFonts)
    if install_ids:
        p1 = re.compile('<setFont name=".*?" ')
        p2 = re.compile('fontName=".*?" ')        
        config_parameter_obj = pooler.get_pool(cr.dbname).get("ir.config_parameter")
        base_font = config_parameter_obj.get_param(cr, uid, "font_url")
        cjk_wrap = config_parameter_obj.get_param(cr, uid, "cjk_wrap")
        fonts_map = []
        if base_font:
            for font in OE_FONTS:
                fonts_map += [(font, 'myFont', base_font, 'all')]
        cfonts.CustomTTFonts = fonts_map          
        ParagraphStyle.defaults['wordWrap'] = cjk_wrap and 'CJK' or ''
        rml = p1.sub('<setFont name="' + 'myFont' + '" ', rml)
        rml = p2.sub('fontName="' + 'myFont' + '" ', rml)
    # change the fontname
    pdf = create_doc(rml, title=self.title)
    cfonts.CustomTTFonts = originCustomTTFonts
    return pdf, report_type

interface.report_rml.create = create
report_sxw.report_sxw.create_single_pdf = create_single_pdf