#!/usr/bin/env python3
import http.server
import http.client
import socketserver, socket
import threading
import traceback
import json, time
import random

services = {}

def add_service(name, address):
	global services
	if name not in services:
		services[name] = []
	services[name].append(address)

def get_service(name):
	global services
	if name in services:
		pos = random.randint(0,len(services[name])-1)
		return services[name][pos]
	else:
		return None

class host_handler(http.server.BaseHTTPRequestHandler):
	def handleProxyRequest(self, path, address, body=None):
		service_conn = http.client.HTTPConnection(address[0], port=address[1])
		service_conn.request("GET", path, headers=self.headers, body=body)
		response = service_conn.getresponse()
		return response

	def do_GET(self):
		service = self.path.split("?", 1)[0]

		address = get_service(service)
		if address is not None:
			print("REDIRECTED:", service, 'Location', "http://"+address[0]+":"+str(address[1]),"\n")
			response = None
			try:
				response = self.handleProxyRequest(self.path, address)
			except:
				print("Error: ", traceback.format_exc())
				host = address[0]
				port = address[1]
				# TODO remove node
				#print("Lost connection to service {} on {}:{}".format(service, host,port))
				#nodes_to_delete.append(node)
				self.send_response(500)
				self.send_header('Content-type','text')
				self.end_headers()
				self.wfile.write("Internal Error".encode())
			finally:
				if response is None:
					return
				body = response.read()
				self.send_response(response.status)
				for (header, value) in response.getheaders():
					self.send_header(header, value)
				self.end_headers()
				self.wfile.write(body)
				print("Done with redirect")
		else:
			print("Unsupported service:", service)
			self.send_response(404)

class register_handler(http.server.BaseHTTPRequestHandler):
	def register(self, message, ip):
		try:
			message = json.loads(message)
			port = int(message['port'])
			add_service(message['name'], (ip,port))
			print("Adding {0}:{1} for service: {2}".format(ip, port, message['name']))
			return None
		except:
			return traceback.format_exc()

	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','json')
		self.end_headers()
		self.wfile.write(json.dumps(services, sort_keys=True, indent=4).encode())

	def do_POST(self):
		#content_length = int(self.headers['Content-Length'])
		content_length = len(self.rfile.peek())
		message = self.rfile.read(content_length).decode("utf-8")
		print("MESSAGE: " + message)
		message = self.register(message, self.client_address[0])
		if (message != None):
			self.send_response(500)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(message.encode())
		else:
			self.send_response(200)
			self.end_headers()

def startHost(port, mode):
	httpd = socketserver.ThreadingTCPServer(("", HOST_PORT), host_handler)
	print("hosting on port", HOST_PORT)
	httpd.serve_forever()

def startRegister(port):
	registerd = socketserver.ThreadingTCPServer(("", REGISTER_PORT), register_handler)
	print("register on port", REGISTER_PORT)
	registerd.serve_forever()

def checkServices():
	while True:
		time.sleep(1)
		services_to_delete = []
		for service in services:
			nodes_to_delete = []
			for node in services[service]:
				try:	
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect(node)
				except:
					host = node[0]
					port = node[1]
					print("Lost connection to service {} on {}:{}".format(service, host,port))
					nodes_to_delete.append(node)
			services[service] = [e for e in services[service] if e not in nodes_to_delete]
			if len(services[service]) == 0:
				print("Removing service: {}".format(service))
				services_to_delete.append(service)
		for service in services_to_delete:
			del services[service]

def main(HOST_PORT, REGISTER_PORT, mode):
	threads = []
	t = threading.Thread(target=startHost, args=(HOST_PORT, mode))
	threads.append(t)
	t.start()
	t = threading.Thread(target=startRegister, args=(REGISTER_PORT,))
	threads.append(t)
	t.start()
	t = threading.Thread(target=checkServices)
	threads.append(t)
	t.start()

if __name__ == "__main__":
	HOST_PORT = 80
	REGISTER_PORT = 9000
	mode = 1
	try:
		main(HOST_PORT, REGISTER_PORT, mode)
	except:
		print("Error: " + traceback.format_exc())