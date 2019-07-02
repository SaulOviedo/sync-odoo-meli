from odoo import models, fields, api

class meliAttr(models.Model):
	_inherit = 'product.attribute'

	meli_id = fields.Char()
