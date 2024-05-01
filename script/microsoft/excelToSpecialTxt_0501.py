import os
import sys
import pandas as pd
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", message="Print area cannot be set to Defined name")

# 表名与标识符映射
sheet_name_map = {"客户信息表": "ENT", "总量额度接口表": "LIM", "产品额度接口表": "FAC"}


def format_amount(val):
    """直接将值转换为字符串并保留三位小数。"""
    return "{:.3f}".format(float(val))


def business_licence_type(val):
    return "33"


def convert_excel_to_txt_integrated(input_file, output_dir):

    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheets_info = [
        ("客户信息表", "ZCB0210D.ENT.now", "GLMS_ENTITY", "A:AC", []),
        ("总量额度接口表", "ZCB0210D.LIM.now", "GLMS_LIMIT_ALL", "B:K", ["I"]),
        ("产品额度接口表", "ZCB0210D.FAC.now", "GLMS_FACILITY_PRODUCT", "B:N", ["L"]),
    ]

    for sheet_name, output_name, tab_name, cols_range, amount_cols in sheets_info:

        # 检查各个sheet是否是需要被转换的
        if sheet_name not in ["客户信息表", "总量额度接口表", "产品额度接口表"]:
            continue

        # 读取Excel工作表的指定列，并获取总行数
        with pd.ExcelFile(input_file, engine="openpyxl") as xls:
            df = pd.read_excel(
                xls,
                sheet_name=sheet_name,
                skiprows=3,
                usecols=cols_range,
                engine="openpyxl",
            )

        # 处理数据框
        if sheet_name == "客户信息表":
            df.iloc[:, 1] = pd.to_datetime(df.iloc[:, 1]).dt.strftime(
                "%Y%m%d"
            )  # B列为日期
            df.iloc[:, 19] = df.iloc[:, 19].apply(
                business_licence_type
            )  # 类型为营业执照时，暂用G6
            df.iloc[:, 23] = df.iloc[:, 23].apply(lambda x: str(x).zfill(3))
            df.iloc[:, 28] = df.iloc[:, 28].apply(lambda x: str(x).zfill(3))
            df.iloc[:, 26] = df.iloc[:, 26].apply(lambda x: str(x).zfill(2))

        if sheet_name == "总量额度接口表":
            df.iloc[:, 1] = pd.to_datetime(df.iloc[:, 1]).dt.strftime(
                "%Y%m%d"
            )  # C列为日期
            df.iloc[:, 8] = pd.to_datetime(df.iloc[:, 8]).dt.strftime(
                "%Y%m%d"
            )  # J列为日期
            df.iloc[:, 9] = pd.to_datetime(df.iloc[:, 9]).dt.strftime(
                "%Y%m%d"
            )  # K列为日期
            df.iloc[:, 7] = df.iloc[:, 7].apply(format_amount)  # I列为金额
            df.iloc[:, 2] = df.iloc[:, 2].apply(lambda x: str(x).zfill(3))
            df = df.dropna(subset=df.columns[[7, 8, 9]], how="any")

        if sheet_name == "产品额度接口表":
            df.iloc[:, 1] = pd.to_datetime(df.iloc[:, 1]).dt.strftime(
                "%Y%m%d"
            )  # C列为日期
            df.iloc[:, 7] = pd.to_datetime(df.iloc[:, 7]).dt.strftime(
                "%Y%m%d"
            )  # I列为日期
            df.iloc[:, 8] = pd.to_datetime(df.iloc[:, 8]).dt.strftime(
                "%Y%m%d"
            )  # J列为日期
            df.iloc[:, 10] = df.iloc[:, 10].apply(format_amount)  # L列为金额
            df.iloc[:, 12] = df.iloc[:, 12].apply(format_amount)  # N列为金额
            df.iloc[:, 2] = df.iloc[:, 2].apply(lambda x: str(x).zfill(3))
            df = df.dropna(subset=df.columns[[7, 8]], how="any")

        num_rows = df.shape[0]
        # print(df)
        # print(num_rows)
        # 将数据框转换为所需的txt格式
        df.fillna(" ", inplace=True)
        df_str = df.apply(lambda x: " | ".join(map(str, x)) + " | ", axis=1).str.cat(
            sep="\n"
        )  # 修改

        # 创建控制信息
        control_info = f"""|||||Begin
    |||||TabName={tab_name}
    |||||Version=2.0.0
    |||||SysID=ZC
    |||||InfCenterID=NULL
    |||||ProvinceOrgID=B0210
    |||||DataStartDate={today}
    |||||DataEndDate={today}
    |||||IncID=0
    |||||RecNum={num_rows}
    |||||Sep=" | "
    |||||GenTime={time_now}
    |||||CycFlag=D
    |||||End"""

        if sheet_name == "客户信息表":
            # 使用UTF-8将内容写入输出目录的txt文件中
            output_path_new = os.path.join(output_dir, output_name)
            print(output_path_new)
            with open(output_path_new, "w", encoding="utf-8") as f:
                f.write(df_str)
                f.write("\n")
                f.write(control_info)
        else:
            # 使用ANSI将内容写入输出目录的txt文件中
            output_path_new = os.path.join(output_dir, output_name)
            print(output_path_new)
            with open(output_path_new, "w", encoding="cp1252") as f:
                f.write(df_str)
                f.write("\n")
                f.write(control_info)


# if __name__ == "__main__":
#     print(sys.argv)
#     # input_file = sys.argv[1]
#     # output_path = sys.argv[2]
#     target_file = "/Users/luoyu/Desktop/codes/工作/GUI/多合一小工具/脱敏报表.xlsx"
#     output_path = "/Users/luoyu/Desktop/codes/工作/GUI/多合一小工具"
#     convert_excel_to_txt_integrated(target_file, output_path)
