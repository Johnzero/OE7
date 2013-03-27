# -*- encoding: utf-8 -*-

import sys
import os

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

xml_temp = """<?xml version="1.0" encoding="utf-8"?>
<openerp>
    <data>
                %s
                </data>
        </openerp>
"""

color_xml = """
<record id="pick_item_color_%s" model="fuguang.picking.item.color">
    <field name="item_id" ref="pick_item_%s"/>
    <field name="color">%s</field>
    <field name="sequence">%s</field>
</record>
"""

color_none_xml = """
<record id="pick_item_color_%s" model="fuguang.picking.item.color">
    <field name="item_id" ref="pick_item_%s"/>
    <field name="color">无_透明</field>
    <field name="sequence">%s</field>
</record>
"""

item_xml = """
<record id="pick_item_%s" model="fuguang.picking.item">
        <field name="category">%s</field>
        <field name="name">%s</field>
        <field name="code">%s</field>
        <field name="sequence">%s</field>
        <field name="uoms" eval="[%s]"/>
        <field name="price">%s</field>
        <field name="volume">%s</field>
</record>
"""

uom_xml = """<record id="pick_item_uom_%s" model="fuguang.picking.item.uom">
            <field name="name">件(%s只)</field>
                <field name="factor">%s</field>
        </record>
"""

uom_tao_xml = """<record id="pick_item_uom_tao_%s" model="fuguang.picking.item.uom">
            <field name="name">件(%s套)</field>
                <field name="factor">%s</field>
        </record>
"""

def gen_xml_new():
    xml = ''
    
    xml_file = open('items.xml','w')
    price_file = open('price_20120423.csv', 'r')
    price_data = {}

    p_list = price_file.readlines()
    price_file.close()

    uom_data_list = []
    for l in p_list:
        if l and ',,,,' not in l:
            l_list = l.strip().split(',')
            if len(l_list) == 6:
                code = l_list[1].strip().replace('型','').replace('--', '-').replace('-', '-') or '无货号'
                uom = l_list[2].strip()
                vol = l_list[3].strip()
                price = l_list[4].strip()
                if uom not in uom_data_list:
                    uom_data_list.append(uom)
                price_data[code] = { 'uom': uom, 'vol':vol, 'price':price}
        
    print 'got price_data', len(price_data)
    for u in uom_data_list:
            if '件' in u:
                if '套' in u:
                    u = u.replace('件(','').replace('套)','')
                    xml = xml + (uom_tao_xml % (u, u, u))
                else:
                    u = u.replace('件(','').replace('只)','')
                
                    xml = xml + (uom_xml % (u, u, u))
            
    csv = open('20120423.csv', 'r')
    lines = csv.readlines()
    csv.close()
    
    item_count = 0
    color_count = 1
    
    last_item_name = ''
    
    for line in lines:
        data = line.strip().split(',')
        category = data[0]
        code = data[2].strip().replace('型','').replace('--', '-').replace('-', '-')
        name = data[1].strip()
        color = data[3].strip()

        if last_item_name != name:
            uoms = ""
            
            us = price_data.get(code)

            s_s = "(6, 0, [ref('base_pick_item_uom'),ref('pick_item_uom_%s')])"
            s_t_s = "(6, 0, [ref('base_pick_item_uom_tao'),ref('pick_item_uom_tao_%s')])"
            if us and us.get('uom'):
                uom_s = us.get('uom')
                if '套' in uom_s:
                    uoms = s_t_s % uom_s.replace('件(','').replace('套)','')
                else:
                    uoms = s_s % uom_s.replace('件(','').replace('只)','')
                item_count = item_count + 1
                
                xml = xml + (item_xml % (item_count, category, name, code, item_count*100, uoms, us.get('price','0'),us.get('vol','')))
                

            last_item_name = name

        if color:
            xml = xml + (color_xml % (color_count, item_count,color.replace(' ', ''), color_count*10))
        else:
            xml = xml + (color_none_xml % (color_count, item_count, color_count*10))
        
        color_count = color_count + 1
    xml_file.write(xml_temp % xml)
    xml_file.close()

gen_xml_new()


def gen_xml():
    xml = ''
    
    xml_file = open('items.xml','w')

    price_file = open('prices.csv', 'r')
    price_data = {}

    p_list = price_file.readlines()
    price_file.close()

    uom_data_list = []
    for l in p_list:
        if l and ',,,,' not in l:
            l_list = l.strip().split(',')
            if len(l_list) == 6:
                code = l_list[1].strip().replace('型','')
                uom = l_list[2].strip()
                vol = l_list[3].strip()
                price = l_list[4].strip()
                if uom not in uom_data_list:
                    uom_data_list.append(uom)
                price_data[code] = { 'uom': uom, 'vol':vol, 'price':price}
                
    print 'got price_data', len(price_data)
    #get uom data:
    for u in uom_data_list:
            if '件' in u:
                u = u.replace('件(','').replace('只)','')
                xml = xml + (uom_xml % (u, u, u))

    csv = open('20120312.csv', 'r')
    lines = csv.readlines()
    csv.close()

    last_item_id = ''
    
    item_count = 1
    color_count = 1
    
    for line in lines:
            line = line.strip()
            if line == ',,,': continue
            
            data = line.split(',')
            
            if len(data) == 4:
                    if '待插入产品' in data:
                            continue
                    if data[1] and data[2]:
                            item_count = item_count + 1
                            color_count = color_count + 1

                            last_item_id = item_count

                            cate = data[0].strip()
                            name = data[1].strip()
                            code = data[2].strip().replace('型','')
                            
                            uoms = ""
                            us = price_data.get(code)
                            s_s = "(6, 0, [ref('base_pick_item_uom'),ref('pick_item_uom_%s')])"
                            if us and us.get('uom'):
                                    uom_s = us.get('uom')
                                    uoms = s_s % uom_s.replace('件(','').replace('只)','')
                                    xml = xml + (item_xml % (item_count, cate, name, code, item_count*100, uoms, us.get('price','0'),us.get('vol','')))
                            else:
                                    print '%s,%s' % (name,code)
                    else:
                            #save color
                            color_count = color_count + 1
                    
                    if data[3]:
                            xml = xml + (color_xml % (color_count, last_item_id, data[3].replace(' ', ''), color_count*10))
                    else:
                            xml = xml + (color_none_xml % (color_count, last_item_id, color_count*10))
            
    xml_file.write(xml_temp % xml)
    xml_file.close()
        
        
#gen_xml()