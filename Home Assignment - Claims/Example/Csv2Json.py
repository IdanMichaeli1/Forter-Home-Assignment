import os
import datetime
import pandas as pd
import numpy as np
from typing import Tuple, List


def set_global_vars() -> None:
    """
    Setup of global variables.
    """
    global \
        ORDER_ID, REASON_CODE, AMOUNT, CURRENCY, \
        PROCESSOR_NAME, DELIVERY_DATE, ORDER_DATE, MERCHANT_NAME, \
        ADDRESS, REASON_CATEGORY, AMOUNT_USD, PROCESSING_DATE
    
    ORDER_ID = 'OrderID'
    REASON_CODE = 'ReasonCode'
    AMOUNT = 'Amount'
    CURRENCY = 'Currency'
    PROCESSOR_NAME = 'ProcessorName'
    DELIVERY_DATE = 'DeliveryDate'
    ORDER_DATE = 'OrderDate'
    MERCHANT_NAME = 'MerchantName'
    ADDRESS = 'Address'
    REASON_CATEGORY = 'ReasonCategory'
    AMOUNT_USD = 'AmountUSD'
    PROCESSING_DATE = 'ProcessingDate'
    
    
def format_reason_codes(reason_codes: pd.DataFrame) -> pd.DataFrame:
    """
    Formats the reason_codes.csv file to match to the input file format.

    Args:
        reason_codes (pd.DataFrame): reason codes csv file.

    Returns:
        pd.DataFrame: formated reason_codes.csv file.
    """
    reason_codes.rename(columns={'Processor': PROCESSOR_NAME, 'Reasoncategory': REASON_CATEGORY}, inplace=True)
    reason_codes.loc[reason_codes[PROCESSOR_NAME] == 'AMERICAN_EXPRESS', PROCESSOR_NAME] = 'AMEX'
    return reason_codes


def set_conditions(df: pd.DataFrame) -> List[pd.Series]:
    """
    Setup of conditions list of pd.Series

    Args:
        df (pd.DataFrame): input df.

    Returns:
        List[pd.Series]: List of conditions.
    """
    conditions = [
        (df[MERCHANT_NAME] == 'MyBook') & (df[PROCESSOR_NAME] == 'VISA'),
        (df[MERCHANT_NAME] == 'MyBook') & (df[PROCESSOR_NAME] == 'AMEX'),
        (df[MERCHANT_NAME] == 'MyFlight') & (df[PROCESSOR_NAME] == 'VISA'),
        (df[MERCHANT_NAME] == 'MyFlight') & (df[PROCESSOR_NAME] == 'AMEX'),
        (df[MERCHANT_NAME] == 'MyShop') & (df[PROCESSOR_NAME] == 'VISA'),
        (df[MERCHANT_NAME] == 'MyShop') & (df[PROCESSOR_NAME] == 'AMEX')
    ]
    
    return conditions


def format_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formats the amount column in the input df as desired in instructions.

    Args:
        df (pd.DataFrame): input df.

    Returns:
        pd.DataFrame: input df with formatted ampunt column.
    """
    conditions = set_conditions(df)
    
    choices = [
        df[AMOUNT] / 100,
        df[AMOUNT] / 1,
        df[AMOUNT] / 1000,
        df[AMOUNT] / 1,
        df[AMOUNT] / 100,
        df[AMOUNT] / 1,
    ]
    
    df[AMOUNT] = np.select(conditions, choices, default=df[AMOUNT]).astype(int)
    return df
    

def add_usd_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds AmoundUSD column to the input df, formatted as desired in instructions.

    Args:
        df (pd.DataFrame): input df.

    Returns:
        pd.DataFrame: input df with AmountUSD column.
    """
    usd_multiplier_map = {
        'EUR': 1/2,
        'USD': 1,
        'AUD': 1/3
    }

    df[AMOUNT_USD] = (df[AMOUNT] * df[CURRENCY].map(usd_multiplier_map)).astype(int)
    return df


def add_processing_date(df: pd.DataFrame, time_delta=3) -> pd.DataFrame:
    """
    Adds processing date column, default set to 3 days from the order date.

    Args:
        df (pd.DataFrame): input df.
        time_delta (int, optional): days of processing. Defaults to 3.

    Returns:
        pd.DataFrame: input df with ProcessingDate column.
    """
    df[PROCESSING_DATE] = df[ORDER_DATE] + datetime.timedelta(time_delta)
    return df


def format_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formats the dates columns in the input df to be formated as desired in the instructions.

    Args:
        df (pd.DataFrame): input df.

    Returns:
        pd.DataFrame: input df with date columns formated.
    """
    df['OrderDatePreprocessed'] = ''
    df['DeliveryDatePreprocessed'] = ''
    df['ProcessingDatePreprocessed'] = ''
    
    conditions = set_conditions(df)

    date_formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%Y"
    ]

    for date_format, condition in list(zip(date_formats, conditions)):
        df.loc[condition, 'OrderDatePreprocessed'] = df.loc[condition, ORDER_DATE].dt.strftime(date_format)
        df.loc[condition, 'DeliveryDatePreprocessed'] = df.loc[condition, DELIVERY_DATE].dt.strftime(date_format)
        df.loc[condition, 'ProcessingDatePreprocessed'] = df.loc[condition, PROCESSING_DATE].dt.strftime(date_format)


    df[ORDER_DATE] = df['OrderDatePreprocessed']
    df[DELIVERY_DATE] = df['DeliveryDatePreprocessed']
    df[PROCESSING_DATE] = df['ProcessingDatePreprocessed']

    df.drop(columns=['OrderDatePreprocessed', 'DeliveryDatePreprocessed', 'ProcessingDatePreprocessed'], inplace=True)
    return df


def get_outputs_filenames(input_path: str) -> Tuple[str]:
    """
    Gets the names of the output file and the duplicates output dile.

    Args:
        input_path (str): input path.

    Returns:
        Tuple[str]: output file, duplicates output file.
    """
    input_file_name: str = os.path.basename(input_path)
    unique_output_file_name = input_file_name.replace('csv', 'json')
    duplicates_output_file_name = input_file_name.replace('.csv', '_duplicates.json')
    
    return unique_output_file_name, duplicates_output_file_name


def export_to_json(df: pd.DataFrame, merchant_name: str, file_name: str) -> None:
    """
    Exports the df to a json file in the 'Outputs' folder with it's file name.
    Create 'Outputs' folder if it isn't exits.

    Args:
        df (pd.DataFrame): input df.
        merchant_name (str): merchant name.
        file_name (str): the file name.
    """
    os.makedirs(f'Outputs/{merchant_name}', exist_ok=True)
    output_path = f'Outputs/{merchant_name}/{file_name}'
    
    with open(output_path, 'w') as f:
        df.to_json(f, indent=4, orient='records')
    
    if 'duplicates' in file_name:
        print(f'The Converted Duplicate Orders JSON file located at:\n{output_path}\n')
    else:
        print(f'The Converted Orders JSON file located at:\n{output_path}\n')
        

def main(file_path: str) -> None:
    """
    Main loop function

    Args:
        file_path (str): path of the input file.
    """
    set_global_vars()
    
    # Get data
    df = pd.read_csv(file_path)
    reason_codes = pd.read_csv("reason codes.csv")
    reason_codes = format_reason_codes(reason_codes)
    
    # Format data
    df = pd.merge(df, reason_codes, how='left', on=[REASON_CODE, PROCESSOR_NAME])
    df = format_amount(df)
    df = add_usd_amount(df)
    df[ORDER_DATE] = pd.to_datetime(df[ORDER_DATE], errors='coerce', dayfirst=True)
    df[DELIVERY_DATE] = pd.to_datetime(df[DELIVERY_DATE], errors='coerce', dayfirst=True)
    df = add_processing_date(df)
    df = format_dates(df)

    # Split data
    df_unique = df.drop_duplicates(subset=ORDER_ID)
    df_duplicates = df[df.duplicated(subset=ORDER_ID)]

    unique_output_file_name, duplicates_output_file_name = get_outputs_filenames(file_path)
    merchant_name = file_path.split('/')[-2]
    
    # Save data
    export_to_json(df_unique, merchant_name, unique_output_file_name)
    export_to_json(df_duplicates, merchant_name, duplicates_output_file_name)
    

if __name__ == '__main__':
    
    while True:
        try:
            file_path = input("Please enter a file path for conversion: \n")
            main(file_path)
            break
        
        except Exception as e:
            print(e)
            continue