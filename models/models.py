# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import exceptions, _
from odoo.exceptions import ValidationError
import json
import base64
import mimetypes
from .meli import Meli
from .meli_odoo_config import *
from . import meli_helper as mh
import logging
_logger = logging.getLogger(__name__)

class productTemplate(models.Model):
	_inherit = 'product.template'

	meli_description = fields.Text(string='Descripción', default='Producto en Perfectas condiciones.')
	meli_status = fields.Char(string='Status', default='NoSync', readonly=True, compute='_depends_meli_id')
	meli_warranty = fields.Char(string='Garantía')
	meli_condition = fields.Selection(selection=[ ("new","Nuevo"), ("used","Usado")] ,string='Condición', default="new")
	meli_id = fields.Char(string='MercadoLibre ID', default='', readonly=False)
	meli_type = fields.Many2one('meli.listing', 'Tipo de Publicación', default=lambda self: self.env['meli.listing'].search([],limit=1))
	product_image_ids = fields.One2many('product.image', 'product_tmpl_id', string='Images')

	def upload_image(self):
		image_ids = []
		company = self.env.user.company_id
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token= company.meli_access_token)
		for image in self.product_image_ids:
			#_logger.info( image.image )
			imagebin = base64.b64decode( image.image )
			files = { 'file': ('image.jpg', imagebin, "image/jpeg") }
			response = meli.upload("/pictures", files, { 'access_token': meli.access_token })
			rjson = response.json()
			#_logger.info( rjson )
			#_logger.info( rjson["id"] )
			image_ids += [{ 'id': rjson["id"]}]
		return image_ids

	@api.one
	def crear(self):
		company = self.env.user.company_id
		meli = Meli(client_id= CLIENT_ID, client_secret= CLIENT_SECRET, access_token= company.meli_access_token)
		conn = mh.check_connection(meli)
		if not conn:
			raise exceptions.except_orm(_('Error'),_('Usuario desconectado.\n Por favor, Inicie sesión.'))
		attributes = []
		for a in self.attribute_line_ids:
			r = a.attribute_id.meli_id
			if r:
				attributes.append({'id':r  , 'value_name': a.value_ids.name})
		_logger.info( attributes )
		img_ids = self.upload_image()
		if img_ids == []:
			raise exceptions.except_orm(_('Error'),_('Su producto debe contener al menos una Imagen.'))
		if self.qty_available == 0:
			raise exceptions.except_orm(_('Error'),_('No hay existencia del producto.\n Por favor, actualice su Inventario.'))
		if self.meli_type == False:
			raise exceptions.except_orm(_('Error'),_('Seleccione un tipo de plublicación para MercadoLibre.'))
		if self.meli_type.type_id == 'free' and self.qty_available != 1:
			raise exceptions.except_orm(_('Error'),_('La cantidad disponible debe ser igual a uno, debido a que es una publicación gratis.\n Por favor, cambie la cantidad o el tipo de publicación.'))
		data = {'title': self.name, 'price': int(self.list_price), 'description':{'plain_text': self.meli_description}, 'attributes': attributes, "pictures": img_ids , "available_quantity": self.qty_available, "listing_type_id": self.meli_type.type_id, "warranty": self.meli_warranty}
		_logger.info(data)
		resp = mh.create_product(meli, company.meli_country, data)

		if resp.status_code >= 200 and resp.status_code < 300:
			self.meli_status = 'Sync'
			self.meli_id = json.loads(resp.content)['id']
		else:
			self.meli_status = 'Error'
			resp = json.loads(resp.content)
			_logger.info( resp )
			raise exceptions.except_orm(_('Error'), resp['cause'][0]['message'])
			
	@api.depends('meli_id')
	def _depends_meli_id(self):
		for r in self:
			if(r.meli_id):
				r.meli_status = 'Sync'
			else:
				r.meli_status = 'NoSync'

	@api.onchange('name')
	def _onchange_name(self):
		company = self.env.user.company_id
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token= company.meli_access_token)
		if self.name :
			category = mh.predict( meli, company.meli_country, {'title':self.name ,'price': self.list_price})
			_logger.info( category['id'] )
			attr = mh.attributes(meli, category['id'])
			_logger.info( attr )
			for attribute in attr:
				_logger.info( attribute)
				found = self.env['product.attribute'].search([('name', '=', attribute)])		
				_logger.info( found )
				if not found:
					res=self.env['product.attribute'].create({'name': attribute, 'type':"select", 'meli_id':attr[attribute]['id']})
					#res=self.env['product.attribute'].create({'name': attribute, 'meli_id':attr[attribute]['id']})
					for value in attr[attribute]['values']:
						self.env['product.attribute.value'].create({'attribute_id':res.id , 'name':value})

			return {
				'warning': {
				'title': _('Información') ,
				'message':'Categoria Encontrada:\n'+category['path']+'\n\n Debe agregar los siguientes Atributos: \n\n-'+'\n -'.join([a for a in attr] or ['Ninguno']) ,
				}
			}

	@api.onchange('meli_type')
	def _onchange_listing_type(self):
		if self.meli_type.type_id == 'free' and self.qty_available != 1:
			return {
				'warning': {
				'title': 'Tipo de Publicacion',
				'message':'La cantidad disponible debe ser igual a uno, debido a que es una publicacion gratis.\n Por favor, cambie la cantidad o el tipo de publicacion.' ,
				}
			}

	@api.constrains('attribute_line_ids')
	def check_attr(self):
		company = self.env.user.company_id
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token= company.meli_access_token )
		category = mh.predict( meli, company.meli_country, {'title':self.name ,'price': self.list_price})
		attr = mh.attributes(meli, category['id'])
		needed = [ a for a in attr]
		found = [ a.attribute_id.name for a in self.attribute_line_ids]
		_logger.info( needed )
		_logger.info( found )
		if not ( set(needed) <= set(found) ):
			raise ValidationError(' Recuerde agregar los siguientes Atributos: \n\n-'+'\n -'.join([a for a in attr] or ['Ninguno']) )

	@api.constrains('name','list_price','qty_available')
	def last_change(self):
		_logger.info('Entre a Update')
		self.meli_update()


	def meli_update(self):
		company = self.env.user.company_id
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token= company.meli_access_token )
		data = {'title': self.name, 'price': int(self.list_price), "available_quantity": self.qty_available}
		if self.meli_id:
			response = meli.put("/items/"+self.meli_id, data, {'access_token':meli.access_token})
			_logger.info(response.content)
