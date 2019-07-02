from odoo import models, fields, api

class ProductImage(models.Model):
    _name = 'product.image'

    name = fields.Char('Name')
    image = fields.Binary('Image', attachment=True)
    product_tmpl_id = fields.Many2one('product.template', 'Related Product', copy=True)
