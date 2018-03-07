import os
import hashlib

DATA_DIR = os.path.join('..', 'crawledData')
REFINED_DATA_DIR = os.path.join('..', 'refinedData')

uniqueContracts = []

for files in sorted(os.listdir(DATA_DIR), key = lambda x : int(x[:-4])):
	if not files.endswith('.sol'):
		continue
	try:
		with open(os.path.join(DATA_DIR, files), 'r') as fp:
			code = fp.read()
			(cn, cl, ch) = (files, len(code), hashlib.md5(code.encode('utf-8')).hexdigest())
			
			if (cl, ch) in [(pl, ph) for (pn, pl, ph) in uniqueContracts]:
				print ('%s is duplicate' % (files))
			else:
				uniqueContracts.append((files, cl, ch))
				with open(os.path.join(REFINED_DATA_DIR, files), 'w') as fp:
					fp.write(code)			
				
	except Exception as e:
		print ("%s\thas problem!!!: %s" % (files, e))
		continue
		
print ('the process has finished')
print ([pn for (pn, pl, ph) in uniqueContracts])
print (len(uniqueContracts))