import os
import pandas as pd
import re
import sys
from datetime import datetime
from dateutil.parser import parse
import gzip
import shutil

# 表名与标识符映射
sheet_name_map = {
    "G01": "GROUP_PROBLEM_LIST",
    "G02": "GROUP_RISK_LIST",
    "G03": "GROUP_KRI_LIST",
    "G04": "GROUP_EXAM_LIST",
    "B01": "BASIC_INFORMATION",
    "B03": "LOCAL_CCY_BOND",
    "B05": "FUND_INVEST",
    "B07": "EQTY_TO_STOCK",
}


def is_valid_date_format(date_str):
    if isinstance(date_str, datetime):
        return date_str.strftime("%Y%m%d")

    patterns = {
        "%Y-%m-%d %H:%M:%S": r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        "%Y-%m %H:%M:%S": r"\d{4}-\d{2} \d{2}:\d{2}:\d{2}",
        "%Y/%m/%d %H:%M:%S": r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}",
        "%Y/%m %H:%M:%S": r"\d{4}/\d{2} \d{2}:\d{2}:\d{2}",
        "%Y-%m-%d": r"\d{4}-\d{2}-\d{2}",
        "%Y-%m": r"\d{4}-\d{2}",
        "%Y/%m/%d": r"\d{4}/\d{2}/\d{2}",
        "%Y/%m": r"\d{4}/\d{2}",
    }
    for fmt, pattern in patterns.items():
        if re.fullmatch(pattern, str(date_str)):
            return fmt


def format_date_columns(df, date_columns):
    for col in date_columns:
        format_type = df[col].apply(lambda x: is_valid_date_format(str(x)))
        # print(format_type)
        if not format_type.isin([False, None]).any():
            df[col] = df[col].apply(
                lambda x: datetime.strptime(str(x), format_type.iloc[0]).strftime(
                    "%Y%m%d"
                )
            )
    return df


def replace_newlines_with_dollar(df):
    # 遍历每一列
    for column in df.columns:
        # 假设每个单元格都是字符串类型
        # 如果不是，可以先转换为字符串
        df[column] = df[column].astype(str).str.replace("\n", "$", regex=False)
    return df


# 转换列标签为从零开始的索引
def column_label_to_index(label):
    index = 0
    for char in label:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1  # 转换为零索引


# 定义一个函数来检查值是否为整数，如果不是，则转换为整数。
def keep_the_integer_state(x):
    if x == "":
        return None
    else:
        y = int(x)
        return y


# 定义一个函数来检查值是否为 float 并四舍五入
def round_if_float(x):
    if isinstance(x, float):
        return round(x, 4)
    return x


def generate_common_info(sheet_name, record_num):
    """根据给定的表名和记录数生成通用信息。"""
    today = datetime.now().strftime("%Y%m%d")
    time_now = datetime.now().strftime("%Y%m%d %H:%M:%S")
    convert_day = "2024-03-31"
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
    filtered_sheet_names = [
        name for name in xls.sheet_names if not re.search("[\u4e00-\u9fff]", name)
    ]
    print(filtered_sheet_names)

    for sheet_name in filtered_sheet_names:
        # 检查各个sheet是否是需要被转换的
        if sheet_name not in sheet_name_map.keys():
            continue

        # 从Excel表中读取数据
        df = pd.read_excel(xls, sheet_name)
        df = df.fillna("")

        # 处理需填充的数据
        if sheet_name == "G01":
            # 定义列标签
            columns_to_process = ["B", "D", "J", "L", "M", "S"]
            column_indices = [
                column_label_to_index(label) for label in columns_to_process
            ]
            # 转换为 Pandas 的零索引并对每列进行操作
            for col in column_indices:
                df.iloc[:, col] = df.iloc[:, col].apply(keep_the_integer_state)
                # 将列转换为 Pandas 的可空整数类型 'Int64' 以处理空值
                df.iloc[:, col] = df.iloc[:, col].astype("Int64")
            # s_column_index = column_label_to_index("S")
            # s_column_description = df.iloc[:, s_column_index]
            # print(s_column_description)
        if sheet_name == "G02":
            # 定义列标签
            columns_to_process = ["D", "E", "F", "G", "H"]
            column_indices = [
                column_label_to_index(label) for label in columns_to_process
            ]
            # 转换为 Pandas 的零索引并对每列进行操作
            for col in column_indices:
                df.iloc[:, col] = df.iloc[:, col].apply(round_if_float)
        if sheet_name == "B01":
            df.iloc[:, 7] = df.iloc[:, 7].astype(str).str.zfill(2)
        if sheet_name == "B03":
            # 定义列标签
            columns_to_process = ["D", "F", "I", "J", "O", "P", "V", "Y", "Z", "AC"]
            column_indices = [
                column_label_to_index(label) for label in columns_to_process
            ]
            # 转换为 Pandas 的零索引并对每列进行操作
            for col in column_indices:
                df.iloc[:, col] = df.iloc[:, col].apply(round_if_float)
        if sheet_name == "B05":
            df.iloc[:, 10] = df.iloc[:, 10].astype(str).str.zfill(6)
            columns_to_process = ["F", "Q"]
            column_indices = [
                column_label_to_index(label) for label in columns_to_process
            ]
            # 转换为 Pandas 的零索引并对每列进行操作
            for col in column_indices:
                df.iloc[:, col] = df.iloc[:, col].apply(round_if_float)
        if sheet_name == "B07":
            columns_to_process = ["D", "E", "F", "J", "K", "P", "Q", "R"]
            column_indices = [
                column_label_to_index(label) for label in columns_to_process
            ]
            # 转换为 Pandas 的零索引并对每列进行操作
            for col in column_indices:
                df.iloc[:, col] = df.iloc[:, col].apply(round_if_float)

        # 格式化日期列
        date_columns = [
            col
            for col in df.columns
            if any(keyword in col for keyword in ["日期", "日", "时间", "期限", "时点"])
        ]

        df = format_date_columns(df, date_columns)

        df = replace_newlines_with_dollar(df)

        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # print(df)
        # print("____________")

        # 首先，使用单字符分隔符导出 DataFrame 为字符串
        data_txt = df.to_csv(
            sep="\x01", index=False, header=False, line_terminator="\x01\n", na_rep=" "
        )

        # 然后，替换单字符分隔符为多字符分隔符
        data_txt = data_txt.replace("\x01", "\x01|\x01")

        # 最后，如果需要，移除末尾多余的分隔符
        data_txt = data_txt.rstrip("\x01|\x01")

        # # 使用|作为分隔符将DataFrame转换为CSV格式的字符串
        # data_txt = "|" + df.to_csv(sep='|', index=False, header=False, line_terminator='|\n|', na_rep=' ').rstrip('|')

        # # 替换|为^A|^A
        # data_txt = data_txt.replace('|', '^A|^A')
        #
        # # 使用正则表达式删除字符串末尾的^A|^A
        # data_txt = re.sub(r'\\^A\\|\\^A$', '', data_txt)

        # print(data_txt)

        # 生成通用信息
        common_info = generate_common_info(sheet_name, len(df))

        # 合并数据和通用信息
        full_txt = data_txt + common_info

        # 写入txt文件
        today = datetime.now().strftime("%Y%m%d")
        # output_file_name = f"AC0004.2B021000.{sheet_name}.{today}0"
        output_file_name = f"ZCB0210D.{sheet_name}.now"
        output_file_path = os.path.join(f"{output_path}/", output_file_name)
        with open(output_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(full_txt)

        # # 将文件进行gzip压缩
        # with open(output_file_path, 'rb') as f_in:
        #     with gzip.open(output_file_path + '.gz', 'wb') as f_out:
        #         shutil.copyfileobj(f_in, f_out)


def process_other_excel_files(input_dir, output_dir):
    """处理输入目录中的所有Excel文件。"""

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        # 检查文件是否为.xlsx文件
        if filename.endswith(".xlsx"):
            file_path = os.path.join(input_dir, filename)
            # 处理Excel文件
            process_excel_file(file_path, output_dir)


# if __name__ == "__main__":
#     print(sys.argv)
#     input_file = sys.argv[1]
#     output_path = sys.argv[2]
#     process_other_excel_files(input_file, output_path)
