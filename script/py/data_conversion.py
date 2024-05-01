import sys
import os
import getopt
import pandas as pd
from RWA_convert_0501 import process_rwa_excel_files, sheet_name_map as rwa_sheet_map
from others_convert_0501 import process_other_excel_files, sheet_name_map as others_sheet_map
from excelToSpecialTxt_0501 import convert_excel_to_txt_integrated, sheet_name_map as credit_limits_sheet_map
# # 假设 Finance 模块也有一个 sheet_name_map
# from finance_module import process_finance, sheet_name_map as finance_sheet_map

def validate_sheet_names(target_path, sheet_name_map):
    for file_name in os.listdir(target_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(target_path, file_name)
            try:
                xls = pd.ExcelFile(file_path)
                sheet_names = xls.sheet_names
                if any(sheet_name in sheet_name_map for sheet_name in sheet_names):
                    return True
            except Exception as e:
                raise Exception(f"Error reading {file_name}: {e}")
    return False


def main(argv):
    input_file = None
    model = None
    data_date = None
    ip_address = None

    # 定义命令行参数
    try:
        opts, args = getopt.getopt(argv, "hi:m:d:p:", ["help", "input=", "model=", "date=", "ip="])
    except getopt.GetoptError:
        print('Usage: data_conversion.py -i <inputfile> -m <model> -d <date> -p <ip>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('Usage: data_conversion.py -i <inputfile> -m <model> -d <date> -p <ip>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-m", "--model"):
            model = arg
        elif opt in ("-d", "--date"):
            data_date = arg
        elif opt in ("-p", "--ip"):
            ip_address = arg

    if not input_file or not model:
        print("Missing required parameters.")
        print('Usage: data_conversion.py -i <inputfile> -m <model> -d <date> -p <ip>')
        sys.exit(2)

    input_files = input_file.split(',')
    target_path = os.path.dirname(input_files[0])

    # 根据模型调用不同的函数
    try:
        if model == 'RWA':
            if validate_sheet_names(target_path, rwa_sheet_map):
                process_rwa_excel_files(target_path, target_path)
                result = "RWA Converted Successfully"
            else:
                raise Exception("Wrong Model")
        elif model == 'Others':
            if validate_sheet_names(target_path, others_sheet_map):
                process_other_excel_files(target_path, target_path)
                result = "Others Converted Successfully"
            else:
                raise Exception("Wrong Model")
        elif model == 'Credit_Limits':
            if validate_sheet_names(target_path, credit_limits_sheet_map):
                convert_excel_to_txt_integrated(input_files[0], target_path)
                result = "Credit Limits Converted Successfully"
            else:
                raise Exception("Wrong Model")
        elif model == 'Finance':
            result = "Building"
            # if validate_sheet_names(target_path, finance_sheet_map):
            #     process_finance(target_path, target_path)
            #     result = "Finance Module Processed Successfully"
            # else:
            #     raise Exception("Wrong Model")
        else:
            raise Exception("Invalid Model")
    except Exception as e:
        print(e)
        sys.exit(1)

    print(result)

if __name__ == "__main__":
    main(sys.argv[1:])

