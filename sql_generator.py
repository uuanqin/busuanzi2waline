"""
将不蒜子中的浏览数据导出为 SQL，以将其迁移至 Waline

作者：wuanqin (wuanqin@mail.ustc.edu.cn)
许可证：MIT
"""
import argparse
import json
import random
import re
import subprocess
import threading
import time
from urllib.parse import urlparse

sitemap = 'sitemap.txt'
output_insesrt_sql = 'out_ins.sql'
output_add_sql = "out_add.sql"
output_add_json = "out_add.json"
output_add_fail_json = "out_add_fail.json"

# Create an ArgumentParser object
parser = argparse.ArgumentParser(epilog="See more information on https://blog.uuanqin.top .")

# Add command line arguments
parser.add_argument("-gi", "--gen_ins", action='store_true', help="生成 SQL 插入字段")
parser.add_argument("-gu", "--gen_upd", action='store_true', help="生成 SQL 更新字段")
parser.add_argument("-r", "--retry", help="重试次数", type=int, default=3)
parser.add_argument("-de", "--delay", help="线程延时时间，随机延时 0.5 ~ n 秒", type=int, default=2)
parser.add_argument("-v", "--verbose", action='store_true', help='输出详尽的处理信息')

# Parse the command line arguments
args = parser.parse_args()
RETRY_TIMES: int = args.retry

# Print function displaying text if option --verbose is used
def printv(*text):
    if args.verbose:
        print(text)

def main():
    # 可以同时进行

    if args.gen_ins:
        print(">>>>>>>>>>>>> 生成 SQL 插入字段 <<<<<<<<<<<<<<<<<<")
        gen_sql_insert_record()

    print()

    if args.gen_upd:
        print(">>>>>>>>>>>>> 生成 SQL 更新字段 <<<<<<<<<<<<<<<<<<")
        gen_sql_update_record()

    print()


def gen_sql_insert_record():
    # 打开文件并按行读取
    with open(sitemap, 'r', encoding='utf-8') as file:
        cnt = 0
        content = ""
        for line in file:
            cnt = cnt + 1
            full_domain,path = extract_domain_and_path(line.strip())
            sql_template = f"INSERT INTO wl_Counter (url, time) " \
                           f"SELECT '{path}', 0 " \
                           f"WHERE NOT EXISTS (SELECT 1 FROM wl_Counter WHERE url = '{path}');\n"
            content = content + sql_template
        print(f"一共处理了{cnt}个网址")

    with open(output_insesrt_sql, 'w') as file:
        file.write(content + '\n')
    print(f"+ 生成的SQL文件为 {output_insesrt_sql}")


def gen_sql_update_record():
    all_url_list = []
    # 打开文件并按行读取
    with open(sitemap, 'r', encoding='utf-8') as file:
        cnt = 0
        for line in file:

            cnt = cnt + 1
            url = line.strip()
            all_url_list.append(url)
        print(f"一共提取了{cnt}个网址")

    # 创建一个空的公共数组
    public_results = []

    # 失败url列表
    public_fails = []

    # 创建一个锁对象
    lock = threading.Lock()

    # 创建线程列表
    threads = []

    # 为每个数据项创建一个线程
    for url in all_url_list:
        # 随机延时
        delay = random.uniform(0.1, args.delay)
        time.sleep(delay)
        thread = threading.Thread(target=task, args=(url, public_results, public_fails, lock))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("All data processed.")
    printv("Public array:", public_results)
    print(f"Success: {len(public_results)}   Fail: {len(public_fails)}")

    content = ""

    for data in public_results:
        sql_statement = f"UPDATE wl_Counter " \
                        f"SET time = IFNULL(time, 0) + {data['page_pv']} " \
                        f"WHERE url = '{data['url']}';\n"
        content += sql_statement

    with open(output_add_sql, 'w') as file:
        file.write(content + '\n')
    print(f"+ 生成的SQL文件为 {output_add_sql}")

    with open(output_add_json, 'w') as file:
        file.write(json.dumps(public_results))
    print(f"+ 生成的Json文件为 {output_add_json}")

    with open(output_add_fail_json, 'w') as file:
        file.write(json.dumps(public_fails))
    print(f"+ 生成的失败网址列表为 {output_add_fail_json}")


def task(url, public_results, public_fails, lock):
    printv(f"Processing {url}")
    curl_command = [
        'curl',
        '-H', f"Referer: {url}",
        '-X', 'GET',  # HTTP 方法，例如 GET, POST 等
        'http://busuanzi.ibruce.info/busuanzi?jsonpCallback=BusuanziCallback_577649258772'  # 目标 URL
    ]
    retry = RETRY_TIMES
    while retry > 0:
        # 随机延时
        delay = random.uniform(0,1 + args.delay*(args.retry-retry)) # 重试策略
        time.sleep(delay)
        retry = retry - 1
        try:
            # 执行 curl 命令并捕获输出
            result = subprocess.run(curl_command, capture_output=True, text=True, check=True)

            # 获取返回的数据
            # 示例：try{BusuanziCallback_1046609647591({"site_uv":21497,"page_pv":2,"version":2.4,"site_pv":38425});}catch(e){}
            response_data = result.stdout
            printv("Response Data:", response_data)
            # 使用正则表达式匹配JSON字符串
            match = re.search(r'\{[^\{\}]*?\}', response_data)
            if match:
                json_str = match.group(0)
                # 将JSON字符串转换为字典
                data_dict = json.loads(json_str)
                full_domain, path = extract_domain_and_path(url.strip())
                data_dict["url"] = path # 因为 Waline 中名为 url 的字段是路径

                with lock:
                    public_results.append(data_dict)
                    print(f"收集到数据 {data_dict} ")
                break
            else:
                printv(f"找不到 Json 字符 - {url} 即将执行可能的重试")


        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running curl: {e}")
            print(f"Error output: {e.stderr}")

    if retry == 0:
        print(f"网址 {url} 的数据获取失败")
        public_fails.append(url)


def extract_domain_and_path(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    domain = parsed_url.netloc
    path = parsed_url.path
    return f"{scheme}://{domain}", path

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
    print("Bye!")
