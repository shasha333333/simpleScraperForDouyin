import pandas as pd

def read_author_urls_from_excel(file_path):
    """
    从 Excel 文件中读取 author_url 列的数据。

    :param file_path: Excel 文件路径
    :return: author_url 列表
    """
    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path)

        # 检查是否存在 author_url 列
        if "链接" in df.columns:
            # 提取 author_url 列的数据
            author_urls = df["链接"].dropna().tolist()  # 去除空值并转换为列表
            return author_urls
        else:
            print(f"Excel 文件中未找到 链接 列")
            return []
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return []
    except Exception as e:
        print(f"读取 Excel 文件时出错: {e}")
        return []


# 示例调用
if __name__ == "__main__":
    # 目标 Excel 文件路径
    excel_file = "目标博主名单.xlsx"

    # 读取 author_url
    author_urls = read_author_urls_from_excel(excel_file)

    # 打印结果
    if author_urls:
        print("读取到的 author_url 列表:")
        for url in author_urls:
            print(url)
    else:
        print("未读取到 author_url")

