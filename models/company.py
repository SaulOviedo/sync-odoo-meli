from odoo import fields, models, api
from odoo.tools.translate import _
from .meli_odoo_config import *
from .meli import Meli
import json
import logging
_logger = logging.getLogger(__name__)


class listing_type(models.Model):
	_name = "meli.listing"

	name = fields.Char( string='Tipo de Publicacion', readonly=True)
	type_id = fields.Char( string='Type ID', readonly=True)

class res_company(models.Model):
	_inherit = "res.company"

	meli_status = fields.Boolean(string='Status', default=False)
	meli_access_token = fields.Char( string='Access Token',size=256, readonly=True)
	meli_refresh_token = fields.Char( string='Refresh Token', size=256, readonly=True)
	meli_country = fields.Selection(selection=[ ("MLA","Argentina"), ("MLB","Brasil"), ("MCO","Colombia"), ("MCR","Costa Rica"), ("MEC","Ecuador"), ("MLM","Mexico"), ("MLU","Uruguay"), ("MLC","Chile"), ("MPA","Panama"), ("MPE","Peru"), ("MRD","Dominicada"), ("MLV","Venezuela")] ,string='Pais de Origen', default="MLV")

	@api.one
	def meli_logout(self):
		self.write({'meli_access_token': False, 'meli_refresh_token': False, 'meli_status': False})
	
	def meli_login(self):
		company = self.env.user.company_id
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
		url_login_meli = meli.auth_url(self.meli_country, redirect_URI=REDIRECT_URI)
		return {
			"type": "ir.actions.act_url",
			"url": url_login_meli,
			"target": "self",
			}

	@api.constrains('meli_country')
	def change_listing_type(self):
		data = self.env['meli.listing'].sudo().search([])
		data.unlink()
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
		resp = meli.get('/sites/'+ self.meli_country +'/listing_types')
		resp = json.loads(resp.content)
		for type in resp:
			found = self.env['meli.listing'].sudo().search([('name','=', type['name'])])
			if not found:
				data.create({'name': type['name'], 'type_id': type['id']})		 


	@api.model
	def refresh(self):
		data = self.env['res.company'].search([])
		for company in data:
			if not company.meli_access_token  or not company.meli_refresh_token:
				_logger.info('No ha iniciado Sesion')
			else:
				_logger.info(' ---Refreshing Token---- ')
				meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token = company.meli_access_token , refresh_token = company.meli_refresh_token)
				meli.get_refresh_token()
				company.write({'meli_access_token' : meli.access_token, 'meli_refresh_token' : meli.refresh_token})
		products = self.env['product.template'].search([('meli_id', '!=','')])
		for p in products:
			p.update()
		_logger.info('------updated all------')	