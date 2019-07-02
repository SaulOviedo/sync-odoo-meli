from odoo import models, fields, api
from odoo import exceptions, _
from odoo.exceptions import ValidationError
import json
from .meli import Meli
from . import meli_helper as mh
from .meli_odoo_config import *
import logging
_logger = logging.getLogger(__name__)


class meli_questions(models.Model):
	_name = "meli.questions"

	name = fields.Char('Pregunta Nro', readonly=True)
	status= fields.Selection( [("ANSWERED","Contestado"), ("UNANSWERED","Sin Contestar")], string='Estado', readonly=True)
	date_created = fields.Date('Fecha', readonly=True)
	item = fields.Many2one( "product.template","Producto", readonly=True)
	question = fields.Text(string='Pregunta', readonly=True)
	answer = fields.Text(string='Respuesta')

	def posting(self):
		company = self.env.user.company_id
		meli = Meli(client_id= CLIENT_ID, client_secret= CLIENT_SECRET, access_token= company.meli_access_token)
		conn = mh.check_connection(meli)
		if not conn:
			raise exceptions.except_orm(_('Error'),_('Usuario desconectado.\n Por favor, Inicie sesión.'))
		if self.answer == '':
			raise exceptions.except_orm(_('Error'),_('La respuesta no debe estar vacia.'))
		data = {'question_id': self.name, 'text': self.answer}
		response = meli.post("/answers", data, {'access_token':meli.access_token})
		if response.status_code == 200:
			self.write({"status" : "ANSWERED"})
			raise exceptions.except_orm(_('Perfecto.'),_('Se ha enviado su respuesta correctamente.'))

