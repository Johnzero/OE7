# -*- coding: utf-8 -*-
##############################################################################
#    Taobao OpenERP Connector
#    Copyright 2013 OSCG
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
##############################################################################

from osv import fields,osv
from taobao_base import TaobaoMixin

class taobao_shop(osv.osv, TaobaoMixin):
    _inherit = "taobao.shop"
    _columns = {
            # taobao user
            'taobao_user_category_id': fields.many2one('res.partner.category', u'淘宝用户分类', select=1, required=True),
            }

    _defaults = {
            }

class res_partner_bank(osv.osv, TaobaoMixin):
    _inherit = "res.partner.bank"

class res_partner(osv.osv, TaobaoMixin):
    _inherit = 'res.partner'

    def _get_taobao_user_profile(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for user in self.browse(cr, uid, ids, context=context):
            res[user.id] = 'http://rate.taobao.com/rate.htm?user_id=%s' % user.taobao_user_id
        return res

    _columns = {
            'taobao_user_id': fields.char(u'用户数字ID', size=64),
            'taobao_nick': fields.char(u'淘宝用户名', size=64),
            'taobao_full_address': fields.char(u'淘宝地址', size=512),
            'taobao_user_profile': fields.function(_get_taobao_user_profile, type='char', string=u'淘宝用户信息'),
            'taobao_receive_sms_remind': fields.boolean(u'接收短信提醒'),
            'taobao_receive_email_remind': fields.boolean(u'接收邮件提醒'),
            }

    _sql_constraints = [('taobao_nick_uniq','unique(taobao_nick)', 'Taobao Nick must be unique!')]

    _defaults = {
            'taobao_receive_sms_remind': False,
            'taobao_receive_email_remind': False,
       }

    def _top_user_get(self, top, nick=None):
        top_user = {'nick':nick }
        return top_user
        fields = ['nick', 'buyer_credit', 'seller_credit',]
        if nick:
            rsp =top('taobao.user.get', nick=nick, fields=fields)
        else:
            rsp =top('taobao.user.get', fields=fields)

        if rsp and rsp.has_key('user'):
            top_user = rsp.user
            if top_user.has_key('buyer_credit'):
                top_user['buyer_credit_level'] = top_user.buyer_credit.level
                top_user['buyer_credit_score'] = top_user.buyer_credit.score
                top_user['buyer_credit_total_num'] = top_user.buyer_credit.total_num
                top_user['buyer_credit_good_num'] = top_user.buyer_credit.good_num
            if top_user.has_key('seller_credit'):
                top_user['seller_credit_level'] = top_user.seller_credit.level
                top_user['seller_credit_score'] = top_user.seller_credit.score
                top_user['seller_credit_total_num'] = top_user.seller_credit.total_num
                top_user['seller_credit_good_num'] = top_user.seller_credit.good_num
            return top_user
        else:
            return None

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
