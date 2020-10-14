import time
from scraper import scrape
import re


def course_info(course):
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return list(filter(None, info))


def course_name(course):
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return [info[0]]


def course_descrip(course):
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return [info[1]]


def course_prereq(course):
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    elif info[2] is None:
        return ['Prerequisites: None']
    return [info[2]]


def course_exclu(course):
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return [info[3]]


def course_breadth(course):
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return [info[4]]


def course_link(course):
    info = scrape(course)
    if info == []:
        return ['Course not found']
    elif len(info) == 1:
        return info
    return [info[5]]


def needed_in(course, code, show_details=True):
    valid = re.compile(r'^[a-zA-Z]{3}$')
    is_valid = re.match(valid, code)
    utsg = re.compile(r'^\w{3}[1-4]\d{2}$')
    utsc = re.compile(r'^\w{3}[A-Da-d]\d{2}$')
    is_utsg = re.match(utsg, course)
    is_utsc = re.match(utsc, course)
    check = False
    out = []
    times = []
    if not is_valid:
        return ['Not a valid course code to search in']
    elif not is_utsg and not is_utsc:
        return ['Not a valid course']
    else:
        for i in range(400):
            to_check = code.upper() + str(i+100)
            if show_details:
                print(to_check)
                start = time.perf_counter()
            prereq = course_prereq(to_check)
            if prereq != 'Course not found' and prereq != 'Not a valid course'\
                    and prereq != 'Prerequisites:\nNone':
                if course in prereq[0]:
                    out.append(to_check)
                check = True
            if show_details:
                end = time.perf_counter()
                print(end-start)
                times.append(end-start)
    if show_details:
        print(sum(times))
        print(sum(times) / 400)
    if not check:
        return [f'No courses starting with {code.upper()}']
    elif out == []:
        return [f'No courses starting with {code.upper()} need {course.upper()}']
    else:
        return out
