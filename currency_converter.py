# project:	Currency Converter
# author:	Bc. Jan Jilecek, janjilecek at gmail.com

import sys, argparse
import json, urllib.request # using only native Python 3 lib is sufficient here
from collections import defaultdict

def checkExceptions(func):
	def functionWrapper(name):
		try:
			func(name)
		except BaseException as e:
			print("Error: " + str(e))
			sys.exit(2)
	return functionWrapper

class CurrencyConverter:
	def __init__(self, base):
		self.outputDict = defaultdict(dict) # output data (dict/json)
		self.base = base # input_currency
		self.out = None # output_currency - default None
		self.amount = 0 
		self.apiUrl = "https://api.fixer.io/latest?base=" # Exchange Rates API URL
		self.symbols = None
		self.data = None # structure for downloaded data

	@checkExceptions
	def getSymbols(self):
		symbolUrl = "https://goo.gl/Gya4qc"
		with urllib.request.urlopen(symbolUrl) as req:
			self.symbols = json.loads(req.read().decode())
		
	def findSymbol(self, symbol):
		foundCurrencies = set()
		for value in self.symbols:
			if self.symbols[value]["symbol_native"] == symbol: 
				foundCurrencies.add((value, self.symbols[value]["name"]))
		return foundCurrencies

	def printAndChooseSymbol(self, currencies):
		if len(currencies) == 1:
			return currencies.pop()[0] # only one tuple in set, we use it then

		for i, curr in enumerate(currencies): # else we present user with all the values
			print(curr[0] + " " + curr[1])

		while True: # continualy check input until its in correct format
			try:
				userInput = input("Please specify the currency by typing its 3 letter code: ")
			except:
				continue
			if userInput not in [x[0] for x in currencies]: # if code not in available codes	
				print("Please choose an existing code from the list.")
				continue
			break
		return userInput

	def printAll(self):
		for key, value in self.data["rates"].items():
			self.outputDict["output"][key] = round(value * self.amount, 2)

	@checkExceptions
	def downloadLatestRates(self): # we get the latest values from our API
		self.getSymbols() # download symbol = name mapping
		found = self.findSymbol(self.base) # search for the input_currency symbol in the map
		if len(found) > 0: self.base = self.printAndChooseSymbol(found) # if multiple hits found, print input prompt 
		with urllib.request.urlopen(self.apiUrl + self.base) as req:
			self.data = json.loads(req.read().decode())

	def help(self): # print basic help
		print ("Parameters: \n--amount - amount which we want to convert - float\n"+
				"--input_currency - input currency - 3 letters name or currency symbol\n"+
				"--output_currency - requested/output currency - 3 letters name or currency symbol\n"+
				"Example:\n"+
				"./currency_converter.py --amount 100.0 --input_currency EUR --output_currency CZK")

	def getArgs(self):
		parser = argparse.ArgumentParser()
		parser.add_argument("--amount", type=float, required=True) # amount should be float, is required
		parser.add_argument("--input_currency", required=True) # input_currency is also not optional
		parser.add_argument("--output_currency")
		try:
			args = parser.parse_args() # parse the arguments
		except:
			print("Error while parsing arguments.")
			sys.exit(2)

		self.out = args.output_currency # save the values from the args structure
		self.amount = args.amount
		self.base = args.input_currency

	def getOutputCurrencyValue(self, val):
		value = self.data["rates"].get(val) # get output_currency from json data
		if self.out == self.base: return self.amount # we convert to same currency
		elif value is None: raise Exception("Unknown output_currency: " + str(val))
		return value

	@checkExceptions
	def convert(self): # Execute the conversion of currencies
		self.outputDict["input"]["amount"] = self.amount
		self.outputDict["input"]["currency"] = self.base
		found = self.findSymbol(self.out) # search for the output_currency symbol in the map
		if len(found) > 0: self.out = self.printAndChooseSymbol(found) # if multiple hits found, print input prompt 

		if self.base == self.out: self.outputDict["output"][self.out] = self.amount
		elif self.out is not None: # if the output_currency value is provided
			value = self.getOutputCurrencyValue(self.out)
			# all is ok, we proceed with the conversion
			self.outputDict["output"][self.out] = round(value * self.amount, 2)
		else: # it is not provided, we print all values
			self.printAll()

		#with open("output.json", 'w') as f: # save to file
		#	json.dump(self.outputDict, f)
		print(json.dumps(self.outputDict, indent=4, sort_keys=True))
		

if __name__ == "__main__":
	cc = CurrencyConverter("CZK") # CZK just a filler
	cc.getArgs()
	cc.downloadLatestRates()
	cc.convert()