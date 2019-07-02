# -*- coding: utf-8 -*-
from odoo import fields, models

class Partner(models.Model):
	_inherit = 'res.partner'

	meli_id = fields.Char( string='ID mercadolibre',size=128, readonly=True)
	meli_nickname = fields.Char( string='Nickname mercadolibre',size=128, readonly=True)
	billing_info = fields.Char( string='Nickname mercadolibre',size=128, readonly=True)