import requests,time,json
from bs4 import BeautifulSoup
from selenium import webdriver

#输入用户信息
User_name = input('请输入NetID：')
Pass_word = input('请输入密码')
student_ID = input('请输入学号')

#获取Cookie
def get_cookie():
    driver = webdriver.Chrome()
    driver.get('http://dean.xjtu.edu.cn/')
    button = driver.find_element_by_xpath(r'/html/body/div[4]/div[1]/div[3]/div[4]/table/tbody/tr[2]/td[1]/a/img')
    button.click()
    time.sleep(1)
    driver.switch_to_window(driver.window_handles[1])
    user_name = driver.find_element_by_xpath(r'//*[@id="form1"]/input[1]')
    user_name.send_keys(User_name)
    pass_word = driver.find_element_by_xpath(r'//*[@id="form1"]/input[2]')
    pass_word.send_keys(Pass_word)
    button_3 = driver.find_element_by_xpath(r'//*[@id="account_login"]')
    button_3.click()
    time.sleep(1)
    cookie = driver.get_cookies()
    driver.switch_to_window(driver.window_handles[0])
    driver.close()
    driver.switch_to_window(driver.window_handles[0])
    driver.close()
    jsonCookies = json.dumps(cookie)
    with open('jwc.json', 'w') as f:
        f.write(jsonCookies)
    with open('jwc.json','r',encoding='utf-8') as f:
        listCookies=json.loads(f.read())
    cookie = [item["name"] + "=" + item["value"] 
    for item in listCookies]
    cookiestr = '; '.join(item for item in cookie)
    return cookiestr

cookies = get_cookie()

#获取token
url_gettoken = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/student/register.do?number='+student_ID
headers_1 = {
    'Cookie':cookies
}
res = requests.get(url_gettoken,headers = headers_1).json()
token = res['data']['token']
headers = {
    'Cookie':cookies,
    'token':token
}

#获取课程信息列表
def get_course_list(headers):
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/programCourse.do'
    data = {
        'querySetting': '{"data":{"studentCode":'+student_ID+',"campus":"1","electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","isMajor":"1","teachingClassType":"FAWKC","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10","pageNumber":"0","order":""}'
    }
    res = requests.post(url,headers = headers,data=data).json()
    courses_list = res['dataList']
    course_list =['']
    count = 1
    for course in courses_list:
        courses = course['tcList']
        for course in courses:
            print(str(count)+'.  ',end = '  ')
            count += 1
            course_list.append(course['teachingClassID'])
            print(course['teacherName'],end = '  ')
            print(course['teachingClassID'],end = '  ')
            print(course['teachingPlace'])
            conflict = course['conflictDesc']
            if conflict:
                print(course['conflictDesc'])
            else:
                print('不冲突')
            print('课程容量'+course['classCapacity'],end = '  ')
            print('已选人数'+course['numberOfSelected'],end = '  ')
            print('剩余名额'+str(int(course['classCapacity'])-int(course['numberOfSelected'])))
            print('-------------------------------------')
    return course_list

#获得可选课程列表
def get_available_course_list(headers):
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/programCourse.do'
    data = {
        'querySetting': '{"data":{"studentCode":'+student_ID+',"campus":"1","electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","isMajor":"1","teachingClassType":"FAWKC","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10","pageNumber":"0","order":""}'
    }
    res = requests.post(url,headers = headers,data=data).json()
    courses_list = res['dataList']
    course_list =['']
    count = 1
    for course in courses_list:
        courses = course['tcList']
        for course in courses:
            conflict = course['conflictDesc']
            if conflict or int(course['classCapacity'])-int(course['numberOfSelected']) < 0:
                continue
            else:
                pass
            print(str(count)+'.  ',end = '  ')
            count += 1
            course_list.append(course['teachingClassID'])
            print(course['teacherName'],end = '  ')
            print(course['teachingClassID'],end = '  ')
            print(course['teachingPlace'])
            if conflict:
                print(course['conflictDesc'])
            else:
                print('不冲突')
            print('课程容量'+course['classCapacity'],end = '  ')
            print('已选人数'+course['numberOfSelected'],end = '  ')
            print('剩余名额'+str(int(course['classCapacity'])-int(course['numberOfSelected'])))
            print('-------------------------------------')
    return course_list

#选课
def select_course(ID,course_list,headers):
    teachingClassId = course_list[ID]
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do'
    param = {
        'addParam': '{"data":{"operationType":"1","studentCode":'+student_ID+',"electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","teachingClassId":'+teachingClassId+',"isMajor":"1","campus":"1","teachingClassType":"FAWKC"}}'
    }
    res = requests.post(url,headers = headers,params=param)
    print('')
    print(res.json()['msg'])
    print('')
    if int(res.json()['code']) == 2:
        return 0
    else:
        return 1
    time.sleep(1)

#退课
def delete_course(ID,my_courses_list,headers):
    teachingClassId = my_courses_list[ID]
    timestamp = str(int(time.time()))
    param = {
        'deleteParam': '{"data":{"operationType":"2","studentCode":'+student_ID+',"electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","teachingClassId":'+teachingClassId+',"isMajor":"1","campus":"1","teachingClassType":"FAWKC"}}',
        'timestamp':timestamp
    }
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/deleteVolunteer.do'
    res = requests.get(url,headers = headers,params = param)
    print('')
    print(res.json()['msg'])
    print('')



# 抢课
def grab_lessons(ID,course_list,headers):
    print('正在持续查询中：')
    teachingClassId = course_list[ID]
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/programCourse.do'
    data = {
        'querySetting': '{"data":{"studentCode":'+student_ID+',"campus":"1","electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","isMajor":"1","teachingClassType":"FAWKC","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10","pageNumber":"0","order":""}'
    }
    times = 1
    while True:
        try:
            res = requests.post(url,headers = headers,data=data).json()
            avialable_course = res['dataList']
            for course in avialable_course:
                detial = course['tcList']
                for member in detial:
                    target_classID = member['teachingClassID']
                    if teachingClassId == target_classID:
                        total_number = int(member['classCapacity'])
                        selected_number = int(member['numberOfSelected'])
                        available_number = total_number - selected_number
                        if available_number >= 1:
                            outcome = select_course(ID,course_list,headers)
                            if outcome == 0:
                                print('容量剩余，但你无法选择此课程')
                                return 0
                            elif outcome == 1:
                                print('抢课成功，查询结束')
                                return 1
                        elif available_number == 0:
                            print('容量已满，继续查询中，已查询次数：',times)
                            times = times + 1
                            time.sleep(1)
                            continue
        except:
            print('网络异常正在重试。。。')
            pass

#查看课表
def show_my_courses(headers):
    timestamp = str(int(time.time()))
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/courseResult.do?timestamp='+timestamp+'&studentCode='+student_ID+'&electiveBatchCode=1a10492bc4054f61a95d4e0be1aa0a15'
    my_courses = requests.get(url,headers = headers).json()
    my_courses = my_courses['dataList']
    print('课程列表')
    my_courses_list = ['']
    count = 1
    for course in my_courses:
        print(str(count)+'.',end = '  ')
        count += 1
        print(course['courseName'],end = '  ')
        print(course['teacherName'],end = '  ')
        print(course['teachingClassID'])
        my_courses_list.append(course['teachingClassID'])
        print('')
    return my_courses_list

#模式选择
mode = input('抢课模式请输入1，选课模式请输入2')

if mode == '1':
    course_list = get_available_course_list(headers)
    ID = int(input('请输入你要抢课的课程编号：'))
    grab_lessons(ID,course_list,headers)
else:
    key = input('输入1查看所有课程，输入2查看可选课程：')
    if key == '1':
        course_list = get_course_list(headers)
    else:
        course_list = get_available_course_list(headers)
    ID = int(input('请输入你要选择的课程编号(退出抢课请输入0）：'))
    if ID == 0:
        pass
    else:
        select_course(ID,course_list,headers)
my_courses_list = show_my_courses(headers)
key = input('输入y进入退选课程，任意键退出')
if key == 'y':
    ID = int(input('请输入要退选的课程序号'))
    delete_course(ID,my_courses_list,headers)
    input('按任意键退出')
else:
    pass