# -*- coding: utf-8 -*-
from odoo import http, fields
import json
from ..models.meli_odoo_config import *
from ..models.meli import Meli
from ..models import meli_helper as mh
import logging
import random
_logger = logging.getLogger(__name__)

class api_test(http.Controller):
	@http.route('/sync/api', type='json', auth='public')
	def meli_api(self, **args):
		company =  http.request.env['res.company'].sudo().search([('meli_access_token','!=',None)],limit=1)
		_logger.info(company)
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=company.meli_access_token)
		code = args.get('resource','none')
		code = code[1:].split('/')
		conn = mh.check_connection(meli)
		_logger.info(args)
		if not conn:
			_logger.info("Json recived, but not connected.")
			return json.dumps({'result':'ok'})
		
		if code[0] == "questions":
				resp = meli.get(args['resource'], {'access_token':meli.access_token})
				resp = json.loads(resp.content)
				item = http.request.env['product.template'].sudo().search([('meli_id','=', resp['item_id'] )],limit=1)
				question = http.request.env['meli.questions'].sudo().search([('name','=', resp['id'] )],limit=1)
				if item and not question:
					detail = {'name': resp['id'], 'status': resp['status'], 'date_created': resp['date_created'], 'item': item.id, 'question':resp['text']}
					http.request.env['meli.questions'].sudo().create(detail)

		elif code[0] == "items":
			_logger.info('-------- testeo ---------')

		elif code[0] == "orders":
			_logger.info('-------- Entro en Order ---------')
			order = http.request.env['sale.order'].sudo().search([('meli_id','=',code[1])],limit=1)
			if order:
				_logger.info('---------Order encontrada---------')
			else:
				_logger.info('---------Order NO encontrada---------')
				resp = meli.get(args['resource'], {'access_token':meli.access_token})
				resp = json.loads(resp.content)
				b = resp['buyer']
				buyer = http.request.env['res.partner'].sudo().search([('meli_id','=', str(b['id']))],limit=1)
				if buyer:
					_logger.info('--------- buyer encontrado ---------')
				else:
					_logger.info('--------- buyer NO encontrado ---------')
					buyer = {'name': b['first_name']+' '+b['last_name'], 'meli_id': str(b['id']), 'meli_nickname': b['nickname'], 'email': b['email'] ,
						'phone': b['phone']['extension']+' '+b['phone']['area_code']+'-'+b['phone']['number'], 'billing_info': b['billing_info']['doc_number'], 'is_company':False}
					buyer = http.request.env['res.partner'].sudo().create(buyer)
					_logger.info(buyer)
				
				detail = {'name': 'ML'+code[1], 'meli_id': code[1],'partner_id': buyer.id, 'state':'sale', 'invoice_status':'to invoice',
					 'confirmation_date': fields.Datetime.now(), 'date_order': fields.Datetime.now()}
				order = http.request.env['sale.order'].sudo().create(detail)
				items = resp['order_items']
				line_env = http.request.env['sale.order.line']
				for item in items:
					product = http.request.env['product.template'].sudo().search([('meli_id','=', item['item']['id'] )],limit=1)
					if product:
						product_detail = {'product_id': product.product_variant_ids.id, 'name': product.product_variant_ids.name ,'order_id': order.id, 'product_uom_qty' : item["quantity"] }
						new_line = line_env.sudo().create(product_detail)
						new_line.product_id_change()
					else:
						order.unlink()
				order.write({'invoice_status':'to invoice'})
		return json.dumps({'result':'ok'})
		
	@http.route('/sync/login', type='http', auth='user', website=True)
	def index(self, **kw):
		code = kw.get('code','none')
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
		if code != 'none':
			meli.authorize( code, REDIRECT_URI)
			_logger.info( meli.access_token)
			company = http.request.env.user.company_id
			_logger.info( company )
			company.write({'meli_access_token' : meli.access_token, 'meli_refresh_token' : meli.refresh_token, 'meli_status': True})
			return http.request.render('sync-odoo-meli.login', {})
		else:
			return http.request.render('sync-odoo-meli.nocode', {})
