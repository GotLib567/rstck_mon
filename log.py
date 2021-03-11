def log(tag, text):
	if(tag == 'i'):
		print("[INFO] " + text)
	elif(tag == 'e'):
		print("[ERROR] " + text)
	elif(tag == 's'):
		print("[SUCCESS] " + text)