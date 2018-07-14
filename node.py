#!/usr/bin/env python3
import http.server
import http.client
import socketserver
import json, sys

global_port = 0
class host_handler(http.server.BaseHTTPRequestHandler):
	def get_content(self):
		global global_port
		return "TEST on port={}\n".format(global_port).encode()

	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text')
		self.end_headers()
		self.wfile.write(self.get_content())

def runner(hoster, host, service):
	global global_port
	httpd = socketserver.ThreadingTCPServer(("", 0), hoster)
	port = httpd.socket.getsockname()[1]
	print("hosting on port", port)
	global_port = port
	conn = http.client.HTTPConnection(host, 9000)
	message = json.dumps({"name":service, "port":port})
	conn.request("POST", "/", message)
	response = conn.getresponse()
	print("Response to registration:", response.status, response.reason)
	print("Message:", response.read())
	conn.close()
	httpd.serve_forever()

if __name__ == "__main__":
	host = "localhost"
	service = "/"
	if len(sys.argv) >= 2:
		host = sys.argv[1]		
	if len(sys.argv) >= 3:
		service = sys.argv[2]
	runner(host_handler, host, service)