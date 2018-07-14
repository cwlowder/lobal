#!/usr/bin/env python3
import node
import sys
import json
import http
from urllib.parse import urlparse, parse_qs

permFile = None

class host_handler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		print("PATH:",str(self.path))
		params = parse_qs(urlparse(self.path).query)
		if not permFile and 'file' not in params:
			self.send_response(400)
			self.send_header('Content-type','text')
			self.end_headers()
			self.wfile.write("Please specify a file parameter".encode())
			return
		try:
			#print("Loo(king for file:", self.headers.as_string())
			fileName = permFile or params['file'][0]
			if (fileName.endswith('.ico') or fileName.endswith('.png') or fileName.endswith('.jpg')):
				content_type = 'image'
			elif (fileName.endswith('.html')):
				content_type = 'text/html'
			else:
				content_type = 'text'
			with open(fileName, 'rb') as file:
				self.send_response(200)
				self.send_header('Content-type','text')
				self.end_headers()
				self.wfile.write(file.read())
		except Exception as e:
			print(str(e))
			self.send_response(404)
			self.send_header('Content-type','text')
			self.end_headers()
			self.wfile.write("File not found".encode())
			return "Error: cannot find file".encode()

if __name__ == "__main__":
	host = "localhost"
	service = "/"
	if len(sys.argv) >= 2:
		host = sys.argv[1]
	if len(sys.argv) >= 3:
		service = sys.argv[2]
	if len(sys.argv) >= 4:
		global permFile
		permFile = sys.argv[3]
	node.runner(host_handler, host, service)