import time
from concurrent.futures.thread import ThreadPoolExecutor
from scraper import scrape
import re
from typing import List


def course_info(course: str) -> List[str]:
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return list(filter(None, info))


def course_name(course: str) -> List[str]:
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return [info[0]]


def course_descrip(course: str) -> List[str]:
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return [info[1]]


def course_prereq(course: str) -> List[str]:
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    elif info[2] is None:
        return ['Prerequisites:', None]
    return [info[2]]


def course_exclu(course: str) -> List[str]:
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    elif info[3] is None:
        return ['Exclusion:', None]
    return [info[3]]


def course_breadth(course: str) -> List[str]:
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    elif info[2] is None:
        return ['Breadth Requirements:', None]
    return [info[4]]


def course_link(course: str) -> List[str]:
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return [info[5]]


def _needed_in_check(course: str, code: str, letter: str, n: int, show_details=True) -> List[str]:
    course = course.upper()
    code = code.upper()
    out = []
    check = False
    for j in range(n, 50 + n):
        if j < 10:
            to_check = code + letter + '0' + str(j)
        else:
            to_check = code + letter + str(j)
        if show_details:
            print(to_check)
        prereq = course_prereq(to_check)
        if prereq[0] != 'Course not found' and prereq[0] != 'Not a valid course' \
                and None not in prereq:
            if course in prereq[0]:
                out.append(to_check)
            check = True
    out.append(check)
    return out


def needed_in(course: str, code: str, show_details=True) -> List[str]:
    course = course.upper()
    code = code.upper()
    valid = re.compile(r'^[a-zA-Z]{3}$')
    is_valid = re.match(valid, code)
    utsg = re.compile(r'^\w{3}[1-4]\d{2}$')
    utsc = re.compile(r'^\w{3}[A-Da-d]\d{2}$')
    is_utsg = re.match(utsg, course)
    is_utsc = re.match(utsc, course)
    check = False
    if not is_valid:
        return ['Not a valid course code to search in']
    elif not is_utsg and not is_utsc:
        return ['Not a valid course']
    else:
        start = time.perf_counter()
        if is_utsg:
            with ThreadPoolExecutor(max_workers=8) as executor:
                future1 = executor.submit(_needed_in_check, course, code, '1', 0)
                future2 = executor.submit(_needed_in_check, course, code, '2', 0)
                future3 = executor.submit(_needed_in_check, course, code, '3', 0)
                future4 = executor.submit(_needed_in_check, course, code, '4', 0)
                future5 = executor.submit(_needed_in_check, course, code, '1', 50)
                future6 = executor.submit(_needed_in_check, course, code, '2', 50)
                future7 = executor.submit(_needed_in_check, course, code, '3', 50)
                future8 = executor.submit(_needed_in_check, course, code, '4', 50)
        elif is_utsc:
            with ThreadPoolExecutor(max_workers=8) as executor:
                future1 = executor.submit(_needed_in_check, course, code, 'A', 0)
                future2 = executor.submit(_needed_in_check, course, code, 'B', 0)
                future3 = executor.submit(_needed_in_check, course, code, 'C', 0)
                future4 = executor.submit(_needed_in_check, course, code, 'D', 0)
                future5 = executor.submit(_needed_in_check, course, code, 'A', 50)
                future6 = executor.submit(_needed_in_check, course, code, 'B', 50)
                future7 = executor.submit(_needed_in_check, course, code, 'C', 50)
                future8 = executor.submit(_needed_in_check, course, code, 'D', 50)
        end = time.perf_counter()
        futures = [future1, future2, future3, future4, future5, future6,
                   future7, future8]
        for future in futures:
            if future.result().pop():
                check = True
        out = future1.result() + future5.result() + future2.result() + \
              future6.result() + future3.result() + future7.result() + \
              future4.result() + future8.result()
        if show_details:
            print(end - start)
        if not check:
            return [f'No courses starting with {code}']
        elif out == []:
            return [f'No courses starting with {code} need {course}']
        else:
            return [f'Courses starting with {code} needing {course}:'] + out
       
    
def _split_prereq(course: str):
    prereqs = course_prereq(course)
    if prereqs != 'Course not found' and prereqs != 'Not a valid course' \
            and prereqs != 'Prerequisites: None':
        prereqs = prereqs[0].replace(u'\u200b', '')
        prereqs = prereqs.replace('Prerequisite:\n', '')
        prereqs = prereqs.split(",")
        for i in range(len(prereqs)):
            brackets = prereqs[i].count('(') - prereqs[i].count(')')
            if brackets != 0:
                prereqs[i+1] = ','.join(prereqs[i:i+2])
                prereqs[i] = ''
        prereqs = [item for item in prereqs if item != '']
        for i in range(len(prereqs)):
            prereqs[i] = prereqs[i].split('/')
        for i in range(len(prereqs)):
            for j in range(len(prereqs[i])):
                prereqs[i][j] = prereqs[i][j].split(',')
        return prereqs
    else:
        return None


def _check_group(taken, prereqs, course):
    ut = re.compile(r'(\w{3}[1-4]\d{2})|\w{3}[A-Da-d]\d{2}')
    for req in prereqs:
        check = []
        for group in req:
            group = group.lower()
            thing = re.search(ut, group)
            if thing.group(0) in taken:
                check.append(True)
            else:
                check.append(False)
        if all(check):
            return True
    return False


def can_take(taken: List[str], course: str):
    taken = [x.lower() for x in taken]
    prereqs = _split_prereq(course)
    if prereqs is None:
        return "No prerequisites found"
    else:
        check = []
        for req in prereqs:
            check.append(_check_group(taken, req, course))
        if all(check):
            return "Fulfilled all requirements"
        else:
            out = "Missing:\n"
            for i in range(len(prereqs)):
                if not check[i]:
                    for j in range(len(prereqs[i])):
                        if len(prereqs[i][j]) > 1:
                            prereqs[i][j] = [','.join(prereqs[i][j])]
                        out += prereqs[i][j][0]
                        if j == len(prereqs[i]) - 1:
                            out += '\n'
                        else:
                            out += '/'
            return out

