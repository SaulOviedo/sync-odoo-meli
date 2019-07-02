from odoo import models, fields, api

class meli_buyers(models.Model):
	_name = 'meli.buyers'

	name = fields.Char( string='Nombre')
	buyer_id = fields.Char(string='ID Comprador')
	nickname = fields.Char(string='Usuario')
	email = fields.Char(string='Email')
	phone = fields.Char( string='Telefono')
	alternative_phone = fields.Char( string='Telefono Alternativo')
	billing_info = fields.Char( string='Facturacion')
	orders = fields.One2many('meli.orders','buyer','Compras' )

class merli_orders(models.Model):
	_name = "meli.orders"

	name = fields.Char('ID Venta', readonly=True)
	status= fields.Selection( [("confirmed","Confirmado"), ("payment_required","Pago requerido"), ("payment_in_process","Pago en proceso"),
                   ("paid","Pagado"),("cancelled","Cancelado")], string='Estado')

	status_detail= fields.Text(string='Detalle de Estado')
	date_created= fields.Date('Fecha de Inicio', readonly=True)
	date_closed= fields.Date('Fecha de Cierre')

	order_items= fields.One2many('meli.order_items','order_id','Item Comprado', readonly=True)
	shipping= fields.Text(string="Envio", readonly=True)

	total_amount= fields.Char(string='Costo Total', readonly=True)
	currency_id= fields.Char(string='Moneda', readonly=True)
	buyer = fields.Many2one( "meli.buyers","Comprador", readonly=True)

class mercadolibre_order_items(models.Model):
	_name = "meli.order_items"

	order_id = fields.Many2one("meli.orders","Order")
	item = fields.Many2one("product.template","Producto")
	order_item_category_id = fields.Char('ID Categoria')
	unit_price = fields.Char(string='Precio Unitario')
	quantity = fields.Integer(string='Cantidad')
#	total_price = fields.Char(string='Total')
#	currency_id = fields.Char(string='Moneda')

class orders(models.Model):
	_inherit = 'sale.order'

	meli_id = fields.Char( string='ID mercadolibre',size=128, readonly=True)