# Contract crawler


This tool can be used for collecting smart contracts on Ethereum for analysis.


[Crawler.py](./crawler.py)
  - It scans and saves Solidity codes of smart contracts on Ethereum from 'https://etherscan.io'
  - By default, 10,000 contracts will be scanned. (See line 35)

[Deduplicator.py](./deduplicator.py)

- It deduplicates redundant contracts saved by the crawler.