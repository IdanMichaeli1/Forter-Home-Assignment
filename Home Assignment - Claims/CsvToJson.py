import csv
import pandas as pd
import json
import os
import datetime

class CsvToJson():
    
    def __init__(self, file_path, reason_codes) -> None:
        
        self.reason_codes = reason_codes
        self.objects = []
        self.duplicated_objects = []
        self.object_IDs = []
        self.days_to_process = 3

        # Read from csv file
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                self.headers = next(reader)
                for row in reader:
                    
                    obj = {}
                    for j, col in enumerate(self.headers):
                        obj[col] = row[j]
                    
                    obj["OrderID"] = int(obj["OrderID"])
                    obj["ReasonCode"] = float(obj["ReasonCode"]) if '.' in obj["ReasonCode"] else int(obj["ReasonCode"])
                    obj["Amount"] = self.format_amount(obj["Amount"], obj["MerchantName"], obj["ProcessorName"])
                    obj["DeliveryDate"] = self.date_convertor(obj["MerchantName"], obj["ProcessorName"], obj["DeliveryDate"])
                    obj["OrderDate"] = self.date_convertor(obj["MerchantName"], obj["ProcessorName"], obj["OrderDate"])
                    obj["ReasonCategory"] = self.reason_category(obj["ReasonCode"], obj["ProcessorName"])                
                    obj["AmountUSD"] = self.usd_convertor(obj["Currency"], obj["Amount"])
                    obj["ProcessingDate"] = self.processing_date(obj["OrderDate"], self.days_to_process)
                    
                    if obj["OrderID"] not in self.object_IDs:
                        self.objects.append(obj)
                        self.object_IDs.append(obj["OrderID"])
                    else:
                        self.duplicated_objects.append(obj)
            
        except (FileNotFoundError, StopIteration, KeyError) as e:
            print("The file path you provided was invalid, try again.")
            file_path = input("Please enter a file path for conversion: \n")
            CsvToJson(file_path, self.reason_codes)
            return
        
        # Write to json files
        input_file = os.path.basename(file_path)
        output_file = input_file.replace("csv", "json")
        duplicates_output_file = input_file.replace(".csv", "_duplicates.json")
        
        if not os.path.exists("Outputs"):
            os.makedirs("Outputs")
            
        with open(f"Outputs/{output_file}", 'w') as output_f:
            json.dump(self.objects, output_f, indent=2, separators=(',', ': '))
        
        with open(f"Outputs/{duplicates_output_file}", 'w') as dup_output_f:
            json.dump(self.duplicated_objects, dup_output_f, indent=2, separators=(',', ': '))
            
    
    def format_amount(self, amount, merchant_name, processor):
        """Returns a formated amount based on the merchant name and processor of an object

        Args:
            amount (str): the amount of an object
            merchant_name (str): the merchant name of an object
            processor (str): the processor name of an object

        Returns:
            int or float: the amount formatted based on its merchant name and processor name
        """
        output_amount = int(amount)
        if processor == "VISA":
            
            if merchant_name == "MyShop":
                output_amount = output_amount / 1000
        
            else :
                output_amount = output_amount / 100
        
        return int(output_amount) if int(output_amount) == output_amount else output_amount
                      
    def date_convertor(self, merchant_name, processor, date) -> str:
        """converte date formats to be in a format of YYYY-MM-DD

        Args:
            merchant_name (str): the merchant name of the object
            processor (str): the processor name of the object
            date (str): the date in it's current format

        Returns:
            str: converted date to a format of YYYY-MM-DD
        """
        if processor == "AMEX":
            try:
                date_obj = datetime.datetime.strptime(date, "%d-%m-%Y").date()
            except ValueError:
                date_obj = datetime.datetime.strptime(date, "%d/%m/%Y").date()
            return date_obj.strftime("%Y-%m-%d")

        elif merchant_name == "MyFlight":
            date_obj = datetime.datetime.strptime(date, "%Y/%m/%d").date()
            return date_obj.strftime("%Y-%m-%d")
        
        return date
        
    def reason_category(self, reason_code, proccessor) -> str:
        """gets the Reason Categoy of an object based on its Reason Code and Processor name

        Args:
            reason_code (int or float): the reason code of an object
            proccessor (str): the processor name of the object

        Returns:
            str: the Reason Category of an object
        """

        proccessor = "AMERICAN_EXPRESS" if proccessor == "AMEX" else proccessor
        matching_rows = self.reason_codes[self.reason_codes["Processor"] == proccessor]
        specific_row = matching_rows[matching_rows["ReasonCode"] == reason_code]
        
        return str(specific_row["Reasoncategory"]).split()[1]
    
    def usd_convertor(self, currency, amount):
        """Returns the amount of an object in USD considering its Merchant name, Processor name
        and curreny.

        Args:
            merchant_name (str): the merchant name of the object
            processor (str): the processor name of the object
            currency (str): the current currency of an object
            amount (int): the amount of monry in its current currency

        Returns:
            int or float: the amount of an object converted to USD
        """
        amountUSD = amount   
        if currency == "EUR":
            amountUSD = amount / 2
        elif currency == "AUD":
            amountUSD = amount / 3
        
        return int(amountUSD) if int(amountUSD) == amountUSD else amountUSD

    def processing_date(self, order_date, days_to_process) -> str:
        """Returns the processing date of an object,
        which is 3 days after the order date.

        Args:
            order_date (str): the order date of an object
            days_to_process (int): the duratiion of the processing in days

        Returns:
            str: the processing date of the object
        """
        curr_dute = datetime.datetime.strptime(order_date, "%Y-%m-%d").date()
        new_date = curr_dute + datetime.timedelta(days_to_process)
        
        return new_date.strftime("%Y-%m-%d")
    
if __name__ == "__main__":
    
    # I assumed that the "reason code.csv" file is within the same folder as this code file
    reason_codes = pd.read_csv("reason codes.csv")
    
    file_path = input("Please enter a file path for conversion: \n")
    CsvToJson(file_path, reason_codes)