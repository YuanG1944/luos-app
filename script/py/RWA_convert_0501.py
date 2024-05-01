import os
import pandas as pd
import sys
import re
from datetime import datetime, time, date
import gzip
import shutil

# 表名与标识符映射
sheet_name_map = {
    "RNT": "ENTITY",
    "RBS": "GL_BALANCE_SHEET",
    "ROB": "ON_OFF_BALANCE",
    "RRO": "PROVISION",
    "RCT": "PROVISION_CONTRACT",
    "REC": "SECURITY",
    "RPT": "SECURITY_POSITION",
    "BFU": "FUND_UNDERLYING",
    "BCG": "ISSURE_CREDIT_RATINGS"
}

# 列选择映射
columns_to_select = {
    "RNT": [1, 2, 3, 4, 5, 6, 7, 11, 17, 19, 22, 24, 25, 26, 28, 29],
    "RBS": [1, 2, 3, 4, 5, 6, 10],
    "ROB": [1, 2, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 16, 17, 21, 25, 34, 38, 39, 40],
    "RRO": [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12],
    "RCT": [1, 2, 3, 4, 5],
    "REC": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 21, 24],
    "RPT": [1, 2, 3, 4, 6, 7, 8, 10, 24],
    "BFU": [1, 2, 3, 4],
    "BCG": [1, 2, 3, 4]
}


def format_date_columns(df, date_columns):
    # 确保 'date_columns' 中的每一列都被解析为 datetime 类型
    for col in date_columns:
        # 检查第一个非NaN元素的类型
        non_na_series = df[col].dropna()
        if len(non_na_series) == 0:
            continue
        # 将 pd.NaT 替换为 None
        df[col] = df[col].apply(lambda x: '' if x is pd.NaT else x)
        # 将日期格式转换为 "YYYYMMDD" 或 "YYYYMM"
        df[col] = pd.to_datetime(df[col], errors='coerce').apply(
            lambda x: x.strftime('%Y%m%d') if x is not None and len(str(x)) >= 19 else x.strftime(
                '%Y%m') if x is not None and len(str(x)) >= 16 else None
        )
    return df

def replace_newlines_with_dollar(df):
    # 遍历每一列
    for column in df.columns:
        # 假设每个单元格都是字符串类型
        # 如果不是，可以先转换为字符串
        df[column] = df[column].astype(str).str.replace('\n', '$', regex=False)
    return df


def generate_common_info(sheet_name, record_num):
    """根据给定的表名和记录数生成通用信息。"""
    today = datetime.now().strftime('%Y%m%d')
    time_now = datetime.now().strftime('%Y%m%d %H:%M:%S')
    convert_day = "2024-03-31"
    # common_info = f'|||diip-control|||{{"TabName":"{sheet_name_map[sheet_name]}", "AssemblyID":"B02100", "PlatformID":"P6", "IsSplitFlag":"0", "MechanismID":"000000", "DataStartDate":"{today}", "DataEndDate":"{today}", "IncID":"1", "RecNum":{record_num}, "Sep":"^A|^A", "CycFlag":"D", "TableGenType":"0", "GenTime":"{time_now}"}}'
    # 创建控制信息
    common_info = f"""|||||Begin
|||||TabName={sheet_name_map[sheet_name]}
|||||Version=2.0.0
|||||SysID=ZC
|||||InfCenterID=NULL
|||||ProvinceOrgID=B0210
|||||DataStartDate={convert_day}
|||||DataEndDate={convert_day}
|||||IncID=0
|||||RecNum={record_num}
|||||Sep="\x01|\x01"
|||||GenTime={time_now}
|||||CycFlag=D
|||||End"""
    return common_info


def process_excel_file(file_path, output_path):
    """处理Excel文件并将处理过的数据写入txt文件。"""
    # 加载Excel文件
    xls = pd.ExcelFile(file_path)

    for sheet_name in xls.sheet_names:
        # 检查各个sheet是否是需要被转换的
        if sheet_name not in sheet_name_map.keys():
            continue

        # 从Excel表中读取数据
        df = pd.read_excel(xls, sheet_name, skiprows=2)
        df = df.fillna('')

        print(sheet_name)

        # # 选择指定的列
        # if sheet_name in columns_to_select:
        #     selected_columns = [col - 1 for col in columns_to_select[sheet_name]]  # 调整为零索引列
        #     df = df.iloc[:, selected_columns]

        # 格式化日期列
        # date_columns = [col for col in df.columns if '日期' in col or col.endswith('日')]
        date_columns = [col for col in df.columns if col.endswith(('日', '日期', '时间', '时点', '期限'))]
        # print(df[date_columns])
        df = format_date_columns(df, date_columns)
        df = df.fillna('')

        df = replace_newlines_with_dollar(df)

        # print(df)

        # print(df.columns)
        # 查看数据
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        # print(df[date_columns])

        # 首先，使用单字符分隔符导出 DataFrame 为字符串
        data_txt = df.to_csv(sep='\x01', index=False, header=False, line_terminator='\x01\n', na_rep=' ')

        # 然后，替换单字符分隔符为多字符分隔符
        data_txt = data_txt.replace('\x01', '\x01|\x01')

        # 最后，如果需要，移除末尾多余的分隔符
        data_txt = data_txt.rstrip('\x01|\x01')

        # # 使用|作为分隔符将DataFrame转换为CSV格式的字符串
        # data_txt = "|" + df.to_csv(sep='|', index=False, header=False, line_terminator='|\n|', na_rep=' ').rstrip('|')
        #
        # # 替换|为^A|^A
        # data_txt = data_txt.replace('|', '^A|^A')
        #
        # # 使用正则表达式删除字符串末尾的^A|^A
        # data_txt = re.sub(r'\\^A\\|\\^A$', '', data_txt)

        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # print(df)
        # print("____________")

        # 生成通用信息
        common_info = generate_common_info(sheet_name, len(df))

        # 合并数据和通用信息
        full_txt = data_txt + common_info

        # 写入txt文件
        today = datetime.now().strftime('%Y%m%d')
        # output_file_name = f"AC0004.2B021000.{sheet_name}.{today}0"
        output_file_name = f"ZCB0210D.{sheet_name}.now"
        # output_file_path = os.path.join('RWA_output', output_file_name)  # 输出文件路径
        output_file_path = os.path.join(f'{output_path}/', output_file_name)
        with open(output_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(full_txt)

        # # 将文件进行gzip压缩
        # with open(output_file_path, 'rb') as f_in:
        #     with gzip.open(output_file_path + '.gz', 'wb') as f_out:
        #         shutil.copyfileobj(f_in, f_out)



def process_rwa_excel_files(input_dir, output_dir):
    """处理输入目录中的所有Excel文件。"""

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        # 检查文件是否为.xlsx文件
        if filename.endswith('.xlsx'):
            file_path = os.path.join(input_dir, filename)
            # 处理Excel文件
            process_excel_file(file_path, output_dir)


# if __name__ == "__main__":
#     print(sys.argv)
#     input_file = sys.argv[1]
#     output_path = sys.argv[2]
#     process_rwa_excel_files(input_file, output_path)
