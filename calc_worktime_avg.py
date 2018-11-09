import json, requests, time
from datetime import datetime

URL = '***'

def calc_avg_work_hours(month: int, cookies: str):
    print("==========平均工时计算开始=========")
    #cookies_dict: dict = parse_cookies(cookies)
    cookies_dict: dict = extract_cookies(cookies)
    print("cookies字典: {}".format(json.dumps(cookies_dict)))
    if month == 0: 
        print("计算日期: 本年度")
        print("本年度平均工时结果: {}小时/天".format(round(year_average(cookies_dict), 2)))
    else:
        print("计算日期: {}月份".format(month))
        print("本月平均工时结果: {}小时/天".format(round(month_average(cookies_dict, month), 2)))


def year_average(cookies_dict: dict) -> float:
    year = datetime.now().year
    month = datetime.now().month
    sum, count = 0.0, 0
    for monthNo in range(1, month+1):
        sum_tmp, count_tmp = month_sum(cookies_dict, monthNo)
        sum += sum_tmp
        count += count_tmp
    return sum / count
    
def month_sum(cookies_dict: dict, month: int) -> tuple:
    data: dict = {"month": get_month_timestamp(month)}
    print("请求body: {}".format(json.dumps(data)))
    headers: dict = {"Content-Type": "application/json"}
    response = requests.post(URL, data=json.dumps(data), headers=headers, cookies=cookies_dict)
    content = json.loads(response.content)
    days = content["data"]["day"]
    sum, count = 0.0, 0
    for each in days:
        start_time = each["startTime"]
        end_time = each["endTime"]
        if start_time == None or end_time == None:
            continue
        delta = (end_time - start_time) / (1000 * 3600)
        sum += delta
        count += 1
    print("{}月总工时: {}小时，天数: {}天".format(month, round(sum, 2), count))
    return sum, count

def month_average(cookies_dict: dict, month: int) -> float:
    sum, count = month_sum(cookies_dict, month)
    return sum / count

def init() -> tuple:
    print("请输入月份(不输入默认计算本年度工时平均值): ")
    month = str_to_int(input())
    print("请输入cookie(使用; 隔开):")
    cookie = input()
    return month, cookie

def get_month_timestamp(month: int) -> int:
    year = datetime.now().year
    if month < 10:
        month_str = "0{}".format(month)
    else:
        month_str = str(month)
    timestr: str = "{year}-{month}-01 00:00:00.000".format(year=year, month=month_str)
    datatime_obj = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
    return int(time.mktime(datatime_obj.timetuple()) * 1000.0 + datatime_obj.microsecond / 1000.0)

def extract_cookies(cookies: str) -> dict:
    return {l.split("=")[0]:l.split("=")[1] for l in cookies.split("; ")}

def str_to_int(month: str) -> int:
    if month == "" or month == None:
        return 0;
    else:
        return int(month)

if __name__ == "__main__":
    month, cookie = init()
    calc_avg_work_hours(month, cookie)
