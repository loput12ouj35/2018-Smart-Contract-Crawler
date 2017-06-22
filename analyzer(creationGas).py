import os

COV_DIR = os.path.join(os.getcwd(), 'originalData')

'''
# line counter
result = {}

for files in os.listdir(COV_DIR):
	if not 'sol' in files:
		continue
	fp = open(os.path.join(COV_DIR, files), 'rb')
	loc = 0
	for line in fp:
		if (line.startswith('//')):
			continue
		if (not line.strip()):
			continue
		loc += 1
		
	result[files] = loc

fp2 = open(os.path.join(os.getcwd(), 'result.csv'), 'wb')
for k, v in result.iteritems():
	fp2.write(str(k) + '\t' + str(v) + '\n')
'''

# creation gas extractor
fp2 = open(os.path.join(os.getcwd(), 'result.csv'), 'wb')
for files in os.listdir(COV_DIR):
	if not 'txt' in files:
		continue
	fp = open(os.path.join(COV_DIR, files), 'rb')
	for line in fp:
		if (line.startswith('Creation: ')):
			fp2.write(files + ': ' + line[8:] + '\n')
		

