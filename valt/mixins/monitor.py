import time
import threading


class valt_monitor:
	def check_room_status(self):
		while not self.kill_threads:
			self.logger.debug(__name__ + ": Thread ID:" + str(threading.get_ident()))
			self.logger.debug(__name__ + ": " + "Room Check Loop: " + str(self.run_check_room_status))
			if self.run_check_room_status:
				self.update_room_status()
			time.sleep(self.room_check_interval)

	def update_room_status(self):
		self.logger.debug(__name__ + ": " + "Room Check Loop: " + "Access Token: " + str(self.accesstoken))
		if self.accesstoken != 0 and self.selected_room != None:
			temp_room_status = self.getroomstatus(self.selected_room)
			if temp_room_status != self.selected_room_status:
				self.selected_room_status = temp_room_status
			if temp_room_status != 0 and temp_room_status != 99 and self.errormsg != None:
				self.logger.debug(__name__ + ": Clear Error")
				self.errormsg = None
				self.selected_room_status = temp_room_status
			self.logger.debug(__name__ + ": " + "Checking Room " + str(self.selected_room) + " current status is " + str(self.selected_room_status))

	def start_room_check_thread(self):
		# if self.selected_room != None and self.selected_room != "":
		self.kill_threads = False
		self.run_check_room_status = True
		self.logger.debug(__name__ + ": " + "Room Check Thread Started")
		if not hasattr(self,'room_check_thread'):
			self.room_check_thread = threading.Thread(target=self.check_room_status)
			self.room_check_thread.daemon = True
			self.room_check_thread.start()
		else:
			self.update_room_status()

	def stop_room_check_thread(self):
		self.run_check_room_status = False
	@property
	def selected_room_status(self):
		return self._selected_room_status
	@selected_room_status.setter
	def selected_room_status(self,new_status):
		self._selected_room_status = new_status
		for callback in self._observers:
			callback(self._selected_room_status)
		self.logger.debug(__name__ + ": " + str(self.selected_room) + ' status updated to ' + str(new_status))
	def bind_to_selected_room_status(self,callback):
		self._observers.append(callback)
	def unbind_to_selected_room_status(self,callback):
		self._observers.remove(callback)
