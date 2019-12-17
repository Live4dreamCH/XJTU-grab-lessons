import requests,time
from bs4 import BeautifulSoup
#获取Cookie
# cookies =
#获取token
cookies = 'JSESSIONID=ih2H9qLSDB-6aoF9KKNkOwaKghtfjsYr7fQoK9Ea1OeaYnhpcrAg!-1064408887; MOD_AMP_AUTH=MOD_AMP_9621c4f0-56cb-46ed-b3e4-9f9afb8d375e; AUTHTGC="i0mHwbJMfoZCGprVjaZZ33PGwMqDN1/f/eCPovgcp7vnlOH3ik9RAQ=="; _WEU=jlUYXl69xrygQ7cc2AxpwywMVDZNd9yKIjZrOiW1lfKVIX*Jo4PXoj..'
url_gettoken = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/student/register.do?number=2193612793'
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
        'querySetting': '{"data":{"studentCode":"2193612793","campus":"1","electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","isMajor":"1","teachingClassType":"FAWKC","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10","pageNumber":"0","order":""}'
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
        'querySetting': '{"data":{"studentCode":"2193612793","campus":"1","electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","isMajor":"1","teachingClassType":"FAWKC","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10","pageNumber":"0","order":""}'
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
        'addParam': '{"data":{"operationType":"1","studentCode":"2193612793","electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","teachingClassId":'+teachingClassId+',"isMajor":"1","campus":"1","teachingClassType":"FAWKC"}}'
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
        'deleteParam': '{"data":{"operationType":"2","studentCode":"2193612793","electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","teachingClassId":'+teachingClassId+',"isMajor":"1","campus":"1","teachingClassType":"FAWKC"}}',
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
        'querySetting': '{"data":{"studentCode":"2193612793","campus":"1","electiveBatchCode":"1a10492bc4054f61a95d4e0be1aa0a15","isMajor":"1","teachingClassType":"FAWKC","checkConflict":"2","checkCapacity":"2","queryContent":""},"pageSize":"10","pageNumber":"0","order":""}'
    }
    times = 1
    while True:
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

#查看课表
def show_my_courses(headers):
    timestamp = str(int(time.time()))
    url = 'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/courseResult.do?timestamp='+timestamp+'&studentCode=2193612793&electiveBatchCode=1a10492bc4054f61a95d4e0be1aa0a15'
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

key = input('输入1查看所有课程，输入2查看可选课程：')
if key == '1':
    course_list = get_course_list(headers)
else:
    course_list = get_available_course_list(headers)
ID = int(input('请输入你要抢课的课程编号：'))
grab_lessons(ID,course_list,headers)
# ID = int(input('请输入你要选择的课程编号：'))
# select_course(ID,course_list,headers)
# my_courses_list = show_my_courses(headers)
# ID = int(input('请输入要退选的课程序号'))
# delete_course(ID,my_courses_list,headers)