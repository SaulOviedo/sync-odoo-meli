import json
import copy
import logging
_logger = logging.getLogger(__name__)

currency={"MLA":"ARS",
    "MLB":"BRL",
    "MCO":"COP",
    "MCR":"CRC",
    "MEC":"USD",
    "MLC":"CLP",
    "MLM":"MXM",
    "MLU":"UYU",
    "MLV":"VEF",
    "MPA":"PAB",
    "MPE":"PEN",
    "MRD":"DOP" 
}

body={"category_id":"",
    "currency_id":"",
    "available_quantity":1,
    "buying_mode":"buy_it_now",
    "listing_type_id":"bronze",
    "condition":"new",
    "warranty": "1 Mes",
    "pictures":[]    
}

def translate(data):
	basic = copy.deepcopy(body)
	basic.update(data)
	return basic

def create_product(meli,site,data):
	product = translate(data)
	if product['warranty'] == '' or product['warranty'] == False:
		product['warranty'] = None
	product['currency_id'] = currency[site]
	data = [{'title':product['title'], 'price':product['price']}]
	response = meli.post("/sites/"+ site +"/category_predictor/predict", data, {'access_token':meli.access_token})
	category = json.loads(response.content)[0]['id']
	product['category_id']= category
	response = meli.post("/items", product, {'access_token':meli.access_token})
	return response
        

def predict(meli,site,data_all):
	if (('title' in data_all) and ('price' in data_all)):
		data = [{'title':data_all['title'], 'price':data_all['price']}]
	response = meli.post("/sites/"+ site +"/category_predictor/predict", data, {'access_token':meli.access_token})
	response = json.loads(response.content) 
	data = { 'id':response[0]['id'],'path': ' > '.join([stage['name'] for stage in response[0]['path_from_root']  ])}
	return data

def product(meli,item):
	response = meli.get("/items/"+ item, {'access_token':meli.access_token})
	return json.loads(response.content)

def products(meli,site,user_id):
	response = meli.get("/sites/"+ site +"/search", {'seller_id': user_id})
	return json.loads(response.content)['results']

def attributes(meli,category):
	response = meli.get("/categories/"+ category +"/attributes")
	attr = {}
	for dic in json.loads(response.content):
		if ('required' in dic['tags']):
			vals = [d['name'] for d in dic['values']]
			attr[dic['name']] = {'values': list(set(vals)) , 'id':dic['id']}
	return attr

def check_connection(meli):
	response = meli.get("users/me", {'access_token':meli.access_token})
	response = json.loads(response.content)
	return not ( 'error' in response.keys())
