import uuid
import os
import ssl
import http.client
from urllib import error, request
import json
import time

class valt_communication:
	def __init__(self: "VALT", **kwargs):
		super().__init__(**kwargs)
		self.ignore_ssl_errors()
	def ignore_ssl_errors(self: "VALT"):
		if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
			ssl._create_default_https_context = ssl._create_unverified_context
	def send_to_valt(self: "VALT",url,**kwargs):
		self.logger.debug(__name__ + ":" + str(url))
		ctx = ssl.create_default_context()
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE
		if 'values' in kwargs:
			params = json.dumps(kwargs['values']).encode('utf-8')
			self.logger.debug(__name__ + ": " + str(params))
		else:
			params = None
		if 'file_path' in kwargs:
			file_path = kwargs['file_path']
		else:
			file_path = None

		try:
			self.logger.debug(__name__ + ": " + "Sending API call")
			starttime = time.time()
			if file_path is not None and os.path.isfile(file_path):
				file_size = os.path.getsize(file_path)

				# Read the file content
				with open(file_path, 'rb') as f:
					file_content = f.read()

				boundary = uuid.uuid4().hex

				# Headers
				content_type = f'multipart/form-data; boundary={boundary}'
				# The range format is: bytes <start>-<end>/<total>
				# For a full file: 0 to (size - 1) / size
				content_range = f'bytes 0-{file_size - 1}/{file_size}'
				body_parts = []
				# 1. Start with the opening boundary
				body_parts.append(f'--{boundary}'.encode())
				# 2. File headers
				body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"'.encode())
				body_parts.append(b'Content-Type: application/octet-stream')
				# 3. An empty line (CRLF) before the actual data
				body_parts.append(b'')
				# 4. Join parts with CRLF
				payload = b'\r\n'.join(body_parts) + b'\r\n'
				# 5. Add the binary file content and the closing boundary
				payload += file_content + f'\r\n--{boundary}--\r\n'.encode()

				# Create request
				req = request.Request(url, data=payload, method='POST')
				req.add_header('Content-Type', content_type)
				req.add_header('Content-Range', content_range)
				response = request.urlopen(req, context=ctx)

			elif params is not None:
				req = request.Request(url)
				req.add_header('Content-Type', 'application/json')
				response = request.urlopen(req, params, timeout=self.httptimeout,context=ctx)
			else:
				req = request.Request(url)
				response = request.urlopen(req, timeout=self.httptimeout,context=ctx)
			endtime = time.time()
			elapsedtime = endtime - starttime
			self.logger.debug(__name__ + ": " + str(elapsedtime) + " seconds elapsed")
			code = response.getcode()
			self.logger.debug(__name__ + f": {code} Received")
			content_type = response.info().get('Content-Type', '')
			self.logger.debug(__name__ + f" Content-Type received: {content_type}")
		except error.HTTPError as e:
			self.accesstoken = 0
			self.logger.error(__name__ + ": VALT API Call Failed")
			self.handleerror(e)
		except error.URLError as e:
			self.accesstoken = 0
			self.logger.error(__name__ + ": VALT API Call Failed")
			self.handleerror(e)
		except http.client.HTTPException as e:
			self.accesstoken = 0
			self.logger.error(__name__ + ": VALT API Call Failed")
			self.handleerror(e)
		except Exception as e:
			self.accesstoken = 0
			self.logger.error(__name__ + ": VALT API Call Failed")
			self.handleerror(e)
		else:
			try:
				self.logger.debug(__name__ + ": " + str(response))
				data = json.load(response)
			except (json.JSONDecodeError, UnicodeDecodeError):
				self.logger.error(__name__ + ": No JSON data in response.")
			except Exception as e:
				self.handleerror(e)
			else:
				self.logger.debug(__name__ + ": " + str(data))
				return data