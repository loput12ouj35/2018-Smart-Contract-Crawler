from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib import parse
import os

class ContractParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		if self.linkMode and tag == 'a':
			for (key, value) in attrs:
				if key == 'href':
					self.links += [parse.urljoin(self.baseUrl, value)]
		self.flag_contract = not self.linkMode and tag == 'pre' and ('class', 'js-sourcecopyarea') in attrs
				
	def handle_data(self, data):
		if self.flag_contract:
			self.contract += data
		
				
	def tryParsing(self, url, linkMode):
		self.linkMode = linkMode
		self.flag_contract = False
		self.links = []
		self.contract = ''
		self.baseUrl = url
		response = urlopen(Request(url, headers = {'User-Agent': 'Mozilla/5.0'}))
		self.feed(response.read().decode('utf-8'))
		
		return self.contract, self.links
		

DATA_DIR = os.path.join('..', 'crawledData')
ERR_LOG = 'error.txt'

with open(ERR_LOG, 'a') as errFp:
	for index in range(1,401):
		url = 'https://etherscan.io/accounts/c/' + str(index)
		print('crawler is trying: index', index, 'url:', url)
		
		try:
			_, links = ContractParser().tryParsing(url, True)
			
			links = [x + '#code' for x in links if 'address/0x' in x and '#comment' not in x]
			print ('total contracts founded: %d' % len(links))
			
			fileIndex = (index - 1) * 25
			for link in links:
				fileIndex += 1
				try:
					contract, _ = ContractParser().tryParsing(link, False)
					if len(contract) != 0:
						fileName = str(fileIndex) + '.sol'
						with open(os.path.join(DATA_DIR,fileName), 'w') as fp:
							fp.write(contract)
					else:
						errFp.write('CONTRACT %d:\tWARNING: no solidity code founded\n, LINK: %s' % (fileIndex, link))
				except Exception as e2:
					errFp.write('CONTRACT %d:\tERROR!: %s\n' % (fileIndex, e2))
					continue
		except Exception as e:
			errFp.write('LOOP %d:\tERROR!: %s\n' % (index, e))
			continue
	