# CSV to JSON Conversion System

This project implements a basic conversion system that converts CSV formatted files containing rejected orders into JSON format. The system also enriches each order with calculated fields and handles duplicate orders.
<br>
<br>
**The full instructions for the assignment are in a pdf named "Home assignment - Claims"**

## Instructions

To use the conversion system, follow these steps:

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/IdanMichaeli1/Forter-Home-Assignment.git
   cd Forter-Home-Assignment/Home Assignment - Claims
   ```
Install the required dependencies. You need Python and to run this:
   ```bash
   pip install -r requirements.txt
   ```

Run the conversion script:
   ```bash
   python Example/Csv2Json.py
   ```

The script will prompt you to enter the path of the CSV file containing orders.
   ```bash
   Inputs/MyShop/file1.csv
   ```

The converted JSON files will be saved in the Outputs directory:

&nbsp;&nbsp;&nbsp;&nbsp; {file_name}.json: Converted orders with calculated fields.<br>
&nbsp;&nbsp;&nbsp;&nbsp; {file_name}_duplicates.json: Duplicate orders that were filtered out.

## Notes
The conversion system supports three merchants (MyShop, MyBook, MyFlight) and two processors (VISA, AMEX).
ReasonCategory, AmountUSD, and ProcessingDate are calculated fields added to each order during conversion.
The mapping for ReasonCategory is provided in the "reason codes.csv" file.
Conversion of amount to USD takes exchange rates into account.
## Limitations
This project assumes a specific scope of merchants and processors as described in the instructions.
Error handling for file paths and invalid data is minimal in this basic implementation.
Feel free to reach out if you have any questions or need assistance!
