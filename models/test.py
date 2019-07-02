from meli import Meli
import meli_helper as mh

meli = Meli(client_id= 4669479355659461 ,client_secret= "IJX5fYHL99zo6nYWFNiBA7s4DCZODPQA" , access_token= "APP_USR-4669479355659461-112714-aee0f899297f53438eae54206150c96f__L_F__-278083628")
conn = mh.check_connection(meli)
print(conn)