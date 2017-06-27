#type: 'address', 'uint', 'int', 'bool', 'byte', 'string', 'mapping', 'enum', 'struct', 'unit'
import os

DATA_DIR = os.path.join('..', 'refinedData')

##############code extractor############

#remove indent of a string
def removeIndent(input):
	if input.startswith((' ', '\t', '\n')):
		return removeIndent(input[1:])
	else:
		return input

#remove comment
def removeComment(code):
	try:
		lx = code.index('//')
		rx = code[lx:].index('\n') + lx
		return removeComment(code[:lx] + code[rx:])
			
	except ValueError:
		return removeComment2(code)
				
#remove comment
def removeComment2(code):
	try:
		lx = code.index('/*')
		rx = code.index('*/')
		return removeComment2(code[:lx] + code[rx + 2:])
			
	except ValueError:
		return code

#remove pragma
def removePragma(code):
	code = removeComment(code)
	code = removeIndent(code)
	
	lx = code.find('pragma')
	while lx > -1:
		rx = code[lx:].index(';')
		code = code[:lx] + code[rx + lx + 1:]
		lx = code.find('pragma')
	
	return code
#split blocks: from '{' to '}'	

def splitBlocks(code):
	stack = []
	
	for index, char in enumerate(code):
		if char == '{':
			stack.append(index)
		elif char == '}' and stack:
			start = stack.pop()
			yield ((len(stack), start, index))
			
#remove other depth; pairs are sorted
def selectDepth(code, pairs, targetDepth):
	#first, extract ranges(pairs) whose depths are targetDepth or +1
	slicedParts = []
	sliced = []
	(clx, crx) = (-1, -1)
	for (depth, lx, rx) in pairs:
		if depth == targetDepth:
			if crx != -1:
				sliced.append((clx, crx))
				slicedParts.append(sliced)
				sliced = []
			(clx, crx) = (lx, rx)
		elif depth == targetDepth + 1:
			sliced.append((clx, lx))
			clx = rx
	sliced.append((clx, crx))
	slicedParts.append(sliced)
	
	result = []
	for part in slicedParts:
		tmp = ''
		for (lx, rx) in part:
			candidate = code[lx + 1:rx]
			tmp += candidate
		result.append(tmp)
	
#	print (result)		##########print raw code
	return result

def splitContractName(code, pairs):
	result = []
	contractNames = selectDepth(code, pairs, 0)[0]
	list = contractNames.replace('contract ', '//contract ').replace('library ', '//library ').split('//')
	for line in list:
		if len(line) == 0:
			continue
		words = removeIndent(line).split(' ')
		result.append((words[0], words[1].replace('\n', '')))
		
	return result
	
	
##############patterns##############
(p1, p2, p3_1 , p3_2) = (0, 0, 0, 0)
#pattern 1: count public variables
def pattern1(line):
	if 'constant ' not in line and 'public ' in line:
		global p1
		p1 += 1
		
#pattern 2: count how many over initializings happen
def pattern2(line):
	caseInt = line.startswith('int') or line.startswith('uint') and (' 0' in line or '=0' in line)
	caseString = line.startswith('string') and ('""' in line or "''" in line)
	caseBool = line.startswith('bool') and (' false' in line or '=false' in line)
	
	if caseInt or caseString or caseBool:
		global p2
		p2 += 1
		
#pattern 3: count (uint, int) variables whose type is too big
def pattern3(line):
	if line.startswith('int') or line.startswith('uint'):
		prefix = line[:line.index(' ')].replace('u', '').replace('int', '')
		if '[' in prefix:
			return
		global p3_1
		p3_1 += 1
		if len(prefix) == 0 or int(prefix) == 256:
			global p3_2
			p3_2 += 1	
	
#pattern 4: check


#pattern 5: find variables which never change
	

#####################start##################
totalConuter = 0
declartionCounter = 0
p2Counter = 0
print ("file\tP1\tP2\tP3\tP4\tP5\tType\tName")

for files in sorted(os.listdir(DATA_DIR), key = lambda x : int(x[:-4])):
	if not files.endswith('.sol'):
		continue
#for files in ['9.sol']:
	try:
		with open(os.path.join(DATA_DIR, files), 'r') as fp:
			allCode = '{' + removeIndent(removePragma(fp.read())) + '}'
			#extract blocks. contract & library: depth 0, declaration: depth 1
			pairs = sorted(list(splitBlocks(allCode)), key = lambda x : x[1])
			contractNames = splitContractName(allCode, pairs)
			contractCodes = selectDepth(allCode, pairs, 1)
			
			for codeIndex, code in enumerate(contractCodes):
				totalConuter += 1
				code = code.replace('\r', ';').replace('\n', ';')
				#clear counters
				(p1, p2, p3_1 , p3_2) = (0, 0, 0, 0)
								
				#iterate all code line and find modifer, etc.
				modiferSet = set()
				structSet = set()
				declarationPart = []	
				for codeLine in code.split(';'):
					codeLine = removeIndent(codeLine)
					if len(codeLine) == 0:
						continue
					elif codeLine.startswith('modifier'):
						words = " ".join(codeLine.split()).replace('(', ' ').split(' ')
						modiferSet.add(words[1])
						continue
					elif codeLine.startswith('struct'):
						words = " ".join(codeLine.split()).replace('(', ' ').split(' ')
						structSet.add(words[1])
						continue
					elif codeLine.startswith(('function', 'event', 'public', 'private', 'returns', 'payable', 'constant', 'external', 'internal')):
						continue
					declarationPart.append(codeLine)
				
				num_declaration = len(declarationPart)
				if num_declaration == 0:
					(type, name) = contractNames[codeIndex]
					print ("%s\thas a contract with no declaration\t%s\t%s" % (files, type, name))
					continue
				#exclude modifer, etc.
				for declaration in declarationPart:
					if declaration.startswith(tuple(modiferSet)):
						num_declaration -= 1
						continue			
#					print (declaration)

					#patterns
					pattern1(declaration)
					pattern2(declaration)
					pattern3(declaration)
					
				r1 = float(p1) / num_declaration
				r2 = float(p2) / num_declaration
				r3 = float(p3_2) / p3_1 if p3_1 != 0 else 0
				(type, name) = contractNames[codeIndex]
				
				print ("%s\t%.2f\t%.2f\t%.2f\t\t\t%s\t%s" % (files, r1,  r2, r3, type, name))
				if type != 'library':
					declartionCounter += 1
				if p2 > 0:
					p2Counter += 1
				
	except Exception as e:
		print ("%s\thas problem!!!: %s" % (files, e))
		continue
		

#end part

print ('TOTAL: %d, delc: %d, P2: %d' % (totalConuter, declartionCounter, p2Counter))
#print ('p1: public pattern.\t0.00: no problem, 1.00: high potential')
#print ('p2: initializing pattern.\t0.00: no problem, else: problem')
#print ('p3: type pattern.\t'0.00: low problem, 1.00: high problem')
#print ('p4: packing pattern.\t')
#print ('p5: constant pattern.\t0.00: no problem, else: problem')
#print ('p6: useless variables pattern.\t0.00: no problem, else: problem')