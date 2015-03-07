import json
import socket
import sys

TCP_IP = '127.0.0.1'
TCP_PORT = 50001
BUFFER_SIZE = 2048

rpc_id = 0

wpt_name = 'WayponitName'
insert_wpt = 'WaypointInsert'
current_fpln = list()
current_airport = 'KMIA'

def connect_server():

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((TCP_IP, TCP_PORT))
	return client

def create_rpc_req(method, params, rpc_id):
	rpc_req = dict()
	rpc_req ['jsonrpc'] = '2.0'
	rpc_req ['method'] = method
	rpc_req ['params'] = params
	rpc_req ['id'] = rpc_id
	rpc_str = json.dumps(rpc_req)
	return rpc_str
	
def get_flightplan(client):
	global rpc_id
	global current_fpln
	rpc_id = rpc_id + 1
	rpc_param = dict()
	rpc_param ['route'] = 0
	rpc_str = create_rpc_req(wpt_name, rpc_param, rpc_id)
	print ("send rpc string : " + rpc_str)
	client.send(rpc_str)
	flight_plan_str = client.recv(BUFFER_SIZE)
	print ("receive rpc result : " + flight_plan_str)
	fpln = json.loads(flight_plan_str)
	current_fpln = fpln['result']
	print "Current flight plan:"
	out_str = current_fpln[0]['fix']
	for leg in current_fpln[1:]:
		out_str = out_str + " --> " + current_fpln['fix']
	print out_str

def insert_waypoint(client):
	global current_fpln
	global rpc_id
	global current_airport
	print "Insert new waypoint into the current flight plan"
	new_wpt = raw_input("Enter waypoint ident with ICAO code: \n")
	i = 1
	out_str = str(i) + " : "+ current_fpln[0]['fix'] + "   "
	for leg in current_fpln[1:]:
		i = i + 1
		out_str = out_str + str(i) + " : " + leg['fix'] + "   "
		if i % 10 == 0:
			out_str = out_str + "\n"
	
	from_wpt_id = current_fpln[int(raw_input(out_str + " : \n")) - 1]['LegId']
	rpc_id = rpc_id + 1
	rpc_param = dict()
	rpc_param['airport'] = current_airport
	rpc_param['wpt_type'] = 2
	rpc_param['waypoint'] = new_wpt
	rpc_param['leg_id'] = from_wpt_id
	rpc_str = create_rpc_req(insert_wpt, rpc_param, rpc_id)
	print ("send rpc string : " + rpc_str)
	client.send(rpc_str)
	result_str = client.recv(BUFFER_SIZE)
	print ("receive rpc result : " + result_str)
	
	
def main(argv):
	#connect to server
	client = connect_server()
	#main loop here
	while True:
		get_flightplan(client)
		insert_waypoint(client)
	
if __name__ == "__main__":
	main(sys.argv)