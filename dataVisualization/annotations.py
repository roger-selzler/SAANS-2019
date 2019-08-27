
SERVER = 'saans.ca'
DATAPATH = '/var/www/rawdata/data/'
	
class saans:
	def __init__(self):
		self.subject = 1
		self.session = 1		

	class annotations(saans):
		def __init__(self):
			super().__init__()
			self.json = {''}

		def loadAnnotations(self):
			with open(TEMPFOLDER + os.sep + 'annotations.json',"r") as f:
				ann = json.load(f)
			print(list(ann))
			print(ann)
			self.json = ann

# class Annotations(saans):
# 	def __init__(self):
# 		super().__init__()
# 		self.json = {''}

# 	def loadAnnotations(self):
# 		with open(TEMPFOLDER + os.sep + 'annotations.json',"r") as f:
# 			ann = json.load(f)
# 		print(list(ann))
# 		print(ann)
# 		self.json = ann

