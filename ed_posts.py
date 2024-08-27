from edapi import EdAPI
import re, requests
from datetime import datetime, timedelta
ed = EdAPI()
ed.login()
SANDBOX = 59934
DATA8 = 59844
SEM = "fa24"

class Homework:
    TEMPLATE = """<document version="2.0"><callout type="success"><bold><link href="https://data8.datahub.berkeley.edu/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fdata-8%2Fmaterials-fa24&amp;branch=main&amp;urlpath=tree%2Fmaterials-fa24%2Fhw%2Fhw{0}%2Fhw{0}.ipynb&amp;branch=main">Homework {0}</link></bold><bold> has been released on the <link href="https://www.data8.org/fa24/">course website</link>!</bold></callout><paragraph>It will be due on {1} at 11pm PT. There are also 5 extra points available for submitting it by {2} at 11pm.</paragraph><paragraph>Remember, there are resources to help you with assignments! You can ask for help here on Ed in the threads for each question (see below). Remember to never post your code publicly; please make a private post if you have to post any code. We also encourage you to review the course policies concerning collaboration and academic honesty here.</paragraph> <paragraph>You can also get help at office hours, which the times can be found <link href="https://www.data8.org/fa24/officehours/">here</link>. We highly recommend getting started on the homework earlier, so that if you need help, you can attend OH before the deadline on {1}.</paragraph><paragraph>Check out our <link href="https://www.data8.org/fa24/debugging/">DataHub Guide</link> if you run into any issues working on Jupyter Notebook before posting on Ed. As a reminder, it is your responsibility to make sure the autograder test results in the notebook match the autograder results on Gradescope after you submit.</paragraph><paragraph>Here is a link to a <link href="https://drive.google.com/file/d/16pHDurc5iAL8AWHdNirpk3JOLJIsITAw/view">video</link> on the autograder submission process and a link to a <link href="https://drive.google.com/file/d/1fejDCUsAMgznwrhNjzZgrKBrPiM6JKXe/view">video</link> on the written submission process.</paragraph><paragraph>Here are the links to the individual question post threads. Please post your questions in the relevant thread instead of creating a new thread each time, unless you need to make a private post with your code:</paragraph><list style="bullet">{3}</list><paragraph>You may ask general logistical questions about Homework {4} in this thread.</paragraph></document>"""

    DUE_DATES = {
        1: "9/4",
        2: "9/11",
        3: "9/18",
        4: "9/25",
        5: "10/2",
        6: "10/9",
        7: "10/16",
        8: "10/30",
        9: "11/6",
        10: "11/13",
        11: "11/20",
        12: "11/27",
    }

    @staticmethod
    def get_questions(assignment_num : str):
        url = f"https://raw.githubusercontent.com/data-8/materials-{SEM}/main/hw/hw{assignment_num}/hw{assignment_num}.ipynb"
        hw = requests.get(url).json()["cells"]
        md = [cell for cell in hw if cell["cell_type"] == "markdown"]
        questions = []
        for cell in md:
            for line in cell["source"]:
                if line.strip().startswith("##"):
                    # check if line has \d. in it
                    if re.search(r"\d\.", line):
                        questions.append(line.strip().strip("##.").strip())
        questions = [q.split(".") for q in questions]
        return {q[0].strip(): q[1].strip() for q in questions}

    @staticmethod
    def question_thread_content(assignment_num : str, question_number: int, question_title: str):
        content = f"""
        <document version="2.0"><paragraph>Post your questions about HW {int(assignment_num)}, Question {question_number} here.</paragraph><paragraph><bold>Remember to make a private post if you want to include anything with your code or solution!</bold></paragraph></document>
        """
        return {
            "type": "post",
            "title": f"HW{int(assignment_num)} Question {question_number}: {question_title}",
            "category": "Homework",
            "subcategory": f"Homework {assignment_num}",
            "subsubcategory": None,
            "content": content,
            "is_pinned": False,
            "is_private": False,
            "is_anonymous": False,
            "is_megathread": True,
            "anonymous_comments": True
        }
        
    @staticmethod
    def make_question_threads(assignment_num: str, sandbox=False):
        hw_questions = Homework.get_questions(assignment_num)
        if sandbox:
            ID = SANDBOX
        else:
            ID = DATA8
        post_ids = {}
        for number, question in hw_questions.items():
            post = Homework.question_thread_content(assignment_num, int(number), question)
            post_ids[number] = ed.post_thread(ID, post)["number"]
        return post_ids

    @staticmethod
    def make_main_thread_question_links(hw_num: str, ids : dict):
        questions = ""
        hw_int = int(hw_num)
        for number, post_id in ids.items():
            questions += f"<list-item><paragraph>HW{hw_int} Q{number}: #{post_id}</paragraph></list-item>"
        return questions

    @staticmethod
    def format_dates(date_str):
        # Convert the input string to a datetime object
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        
        # Define a function to get the ordinal suffix for a given day
        def get_ordinal_suffix(day):
            if 10 <= day % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            return suffix

        # Format the input date
        day_of_week = date_obj.strftime("%A")
        month = date_obj.strftime("%B")
        day = date_obj.day
        suffix = get_ordinal_suffix(day)
        formatted_date = f"{day_of_week} {month} {day}{suffix}"
        
        # Get the previous day
        prev_date_obj = date_obj - timedelta(days=1)
        prev_day_of_week = prev_date_obj.strftime("%A")
        prev_month = prev_date_obj.strftime("%B")
        prev_day = prev_date_obj.day
        prev_suffix = get_ordinal_suffix(prev_day)
        formatted_prev_date = f"{prev_day_of_week} {prev_month} {prev_day}{prev_suffix}"
        
        return formatted_date, formatted_prev_date

    @staticmethod
    def generate_content(hw_num, sandbox=True):
        ids = Homework.make_question_threads(hw_num, sandbox=sandbox)
        threads = Homework.make_main_thread_question_links(hw_num, ids)
        due_date = Homework.DUE_DATES[int(hw_num)]
        date = f"{due_date}/2024"
        date, early_date = Homework.format_dates(date)
        content = Homework.TEMPLATE.format(hw_num, date, early_date, threads, int(hw_num))
        return content

    @staticmethod
    def make_post(assignment_num, sandbox=False):
        params = {
            "type": "announcement",
            "title": f"HW {assignment_num} Released",
            "category": "Homework",
            "subcategory": f"Homework {assignment_num}",
            "subsubcategory": None,
            "content": Homework.generate_content(assignment_num, sandbox=sandbox),
            "is_pinned": True,
            "is_private": True,
            "is_anonymous": False,
            "is_megathread": True,
            "anonymous_comments": True
        }
        if sandbox:
            ID = SANDBOX
        else:
            ID = DATA8
        post = ed.post_thread(ID, params)["number"]
        print(f"Posted HW {assignment_num} threads to {ID}")
        print(f"Main thread: {post}")
        
class Project:
    TEMPLATE = """<document version="2.0"><callout type="success"><bold>Project {0} has been released on the <link href="https://www.data8.org/fa24/">website</link>!</bold> We highly recommend starting early.</callout><list style="unordered"><list-item><paragraph><bold>Deadline:</bold> The entire project is <bold>due on {1} at 11:00 pm PT</bold>. There are 5 extra points available for submitting it by {2} at 11:00 pm. Please <bold>start exporting and submitting at least one hour before the deadline</bold> so we can help you troubleshoot submission errors before 11pm. If you do run into issues, <bold>please post on Ed and we will do our best to help you submit before 11pm.</bold></paragraph></list-item><list-item><paragraph><bold>Checkpoint:</bold> <underline>For full credit</underline>, you must complete all the questions up to the checkpoint in the notebook, pass all public autograder tests for those sections, and submit to the Gradescope <bold>Project {0} Checkpoint assignment by {3} at 11:00 pm PT</bold>. <italic>The goal of the checkpoint is for students to have made some progress on the project before the week it's due so we will not be offering extensions on the checkpoint</italic><bold>.</bold></paragraph></list-item><list-item><paragraph><bold>Partners:</bold> You may work with one other partner. Your partner <bold>must</bold> be enrolled in the same lab as you are unless you are explicitly informed otherwise by a GSI. <bold><underline>Only one of you is allowed to submit the project</underline></bold>. On Gradescope, the person who submits should also designate their partner so that both of you receive credit. You may reference<link href="https://drive.google.com/file/d/1POtij6KECSBjCUeOC_F0Lt3ZmKN7LKIq/view?usp=sharing"> this walkthrough video</link> on how to add partners on Gradescope. Contact your Lab TA if you need a partner.</paragraph></list-item><list-item><paragraph><bold>Rules:</bold> Don't share your code with anybody but your partner. You are welcome to discuss questions with other students but don't share the answers. The experience of solving the problems in this project will prepare you for exams (and life). If someone (who is not your partner) asks you for the answer, resist! Instead, you can demonstrate how you would solve a similar problem.</paragraph></list-item><list-item><paragraph><bold>Support:</bold> You are not alone! Come to <underline><link href="https://www.data8.org/fa24/officehours/">office hours</link></underline>, post on Ed, and talk to your classmates. If you want to ask about the details of your solution to a problem, make a private Ed post and the staff will respond. If you're ever feeling overwhelmed or don't know how to make progress, email your TA or tutor for help. You can find contact information for the staff on the <underline><link href="https://www.data8.org/fa24/">course website</link></underline>.</paragraph></list-item></list><callout type="warning">It is <underline>your responsibility</underline> to <bold>make sure the autograder test results in the notebook match the autograder results on Gradescope after you submit.</bold></callout><callout type="error"><bold>Important: if your pages are not correctly assigned and/or not in the correct PDF format by the deadline, we reserve the right to award no points for your written work.</bold></callout><paragraph>Please post any logistical questions below, and post your questions to these threads as you work through the project!</paragraph><list style="bullet">{4}</list></document>"""
    
    @staticmethod
    def OLD_MAKE_POST(assignment_num, sandbox=False):
        params = {
            "type": "announcement",
            "title": f"Project {int(assignment_num)} Released!",
            "category": "Project",
            "subcategory": f"Project {assignment_num}",
            "subsubcategory": None,
            "content": f"Project {assignment_num} has been released on the course website!",
            "is_pinned": False,
            "is_private": True,
            "is_anonymous": False,
            "is_megathread": True,
            "anonymous_comments": True
        }
        if sandbox:
            ID = SANDBOX
        else:
            ID = DATA8
        post_id = ed.post_thread(ID, params)["number"]
        print(f"Project {assignment_num} post created with ID {post_id}")
        
    DUE_DATES = {
        1.5: "7/2",
        1: "7/5",
        2.5: "8/5",
        2: "8/7",
    }

    @staticmethod
    def get_questions(assignment_num : str):
        url = f"https://raw.githubusercontent.com/data-8/materials-{SEM}/main/project/project{assignment_num}/project{assignment_num}.ipynb"
        hw = requests.get(url).json()["cells"]
        md = [cell for cell in hw if cell["cell_type"] == "markdown"]
        questions = []
        for cell in md:
            for line in cell["source"]:
                if line.strip().startswith("# ") and not line.startswith("# Project"):
                    # check if line has \d. in it
                    if re.search(r"\d", line) and "Part" in line:
                        questions.append(line.strip().strip("##.").strip())
        questions = [q.split(":", maxsplit=1) for q in questions]
        return {q[0].strip(): q[1].strip() for q in questions}

    @staticmethod
    def question_thread_content(assignment_num : str, question_number: int, question_title: str):
        content = f"""
        <document version="2.0"><paragraph>Post your questions about Project {int(assignment_num)}, Question {question_number} here.</paragraph><paragraph><bold>Remember to make a private post if you want to include anything with your code or solution!</bold></paragraph></document>
        """
        return {
            "type": "post",
            "title": f"Project {int(assignment_num)} Question {question_number}: {question_title}",
            "category": "Project",
            "subcategory": f"Project {assignment_num}",
            "subsubcategory": None,
            "content": content,
            "is_pinned": False,
            "is_private": False,
            "is_anonymous": False,
            "is_megathread": True,
            "anonymous_comments": True
        }
        
    @staticmethod
    def make_question_threads(assignment_num: str, sandbox=False):
        hw_questions = Project.get_questions(assignment_num)
        if sandbox:
            ID = SANDBOX
        else:
            ID = DATA8
        post_ids = {}
        for number, question in hw_questions.items():
            post = Project.question_thread_content(assignment_num, int(number), question)
            post_ids[number] = ed.post_thread(ID, post)["number"]
        return post_ids

    @staticmethod
    def make_main_thread_question_links(assignment_num: str, ids : dict):
        questions = ""
        for number, post_id in ids.items():
            questions += f"<list-item><paragraph>Project {int(assignment_num)} Q{number}: #{post_id}</paragraph></list-item>"
        return questions

    @staticmethod
    def format_dates(date_str):
        # Convert the input string to a datetime object
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        
        # Define a function to get the ordinal suffix for a given day
        def get_ordinal_suffix(day):
            if 10 <= day % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            return suffix

        # Format the input date
        day_of_week = date_obj.strftime("%A")
        month = date_obj.strftime("%B")
        day = date_obj.day
        suffix = get_ordinal_suffix(day)
        formatted_date = f"{day_of_week} {month} {day}{suffix}"
        
        # Get the previous day
        prev_date_obj = date_obj - timedelta(days=1)
        prev_day_of_week = prev_date_obj.strftime("%A")
        prev_month = prev_date_obj.strftime("%B")
        prev_day = prev_date_obj.day
        prev_suffix = get_ordinal_suffix(prev_day)
        formatted_prev_date = f"{prev_day_of_week} {prev_month} {prev_day}{prev_suffix}"
        
        return formatted_date, formatted_prev_date

    @staticmethod
    def generate_content(assignment_num, sandbox=True):
        ids = Project.make_question_threads(assignment_num, sandbox=sandbox)
        threads = Project.make_main_thread_question_links(assignment_num, ids)
        due_date = Project.DUE_DATES[int(assignment_num)]
        date = f"{due_date}/2024"
        date, early_date = Project.format_dates(date)
        checkpoint_date = Project.DUE_DATES[int(assignment_num) + 0.5]
        content = Project.TEMPLATE.format(assignment_num, date, early_date, checkpoint_date, threads)
        return content

    @staticmethod
    def make_post(assignment_num, sandbox=False):
        params = {
            "type": "announcement",
            "title": f"Project {assignment_num} Released",
            "category": "Project",
            "subcategory": f"Project {assignment_num}",
            "subsubcategory": None,
            "content": Project.generate_content(assignment_num, sandbox=sandbox),
            "is_pinned": True,
            "is_private": True,
            "is_anonymous": False,
            "is_megathread": True,
            "anonymous_comments": True
        }
        if sandbox:
            ID = SANDBOX
        else:
            ID = DATA8
        post = ed.post_thread(ID, params)["number"]
        print(f"Posted HW {assignment_num} threads to {ID}")
        print(f"Main thread: {post}")

class Lab:
    
    TEMPLATE = """<document version="2.0"><callout type="success"><bold><link href="https://data8.datahub.berkeley.edu/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fdata-8%2Fmaterials-fa24&amp;branch=main&amp;urlpath=tree%2Fmaterials-fa24%2Flab%2Flab{0}%2Flab{0}.ipynb&amp;branch=main">Lab {0}</link></bold><bold> has been released on the <underline><link href="https://www.data8.org/fa24/">course website</link></underline>!</bold></callout><paragraph><bold>Lab assignments are designed to introduce you to the programming and statistics concepts you've learned about in the lecture.</bold> Each lab will guide you through a set of problems that allow you to use Python to answer questions with data. The problems in the lab are good preparation for similar (and harder) problems you will see on your homework assignments. If you are enrolled in a regular lab, you will have time each week to work on the lab notebook in your lab section.</paragraph><callout type="warning"><bold>All students</bold> <bold>should submit the lab notebook to <link href="https://www.gradescope.com/courses/798344">Gradescope</link> by the due date listed on the website at 11 PM</bold>. You must attend the first hour of their lab and submit the lab notebook with significant progress for full lab credit.</callout><paragraph><bold>Lab {0} has been released on Gradescope, so feel free to submit it there once you're done!</bold></paragraph><paragraph><bold><underline>Other Important Notes:</underline></bold></paragraph><list style="unordered"><list-item><paragraph><underline><link href="https://drive.google.com/file/d/1j-H2NCyC01SL8P2rkyiz7-AYFXE11HCD/view?usp=drive_link"><bold>Here</bold></link></underline> is the video for how to submit to Gradescope.</paragraph></list-item><list-item><paragraph>You will not see your grade on Gradescope until we release grades. After you submit to Gradescope, you should see "-/100".</paragraph></list-item><list-item><callout type="info"><bold>!! IT IS EXTREMELY CRITICAL THAT YOU PASS THE SAME TESTS YOU PASSED IN YOUR NOTEBOOK AS GRADESCOPE !!</bold></callout></list-item><list-item><paragraph>Around the 2:50 mark in the video linked above, you can see what "passing" a test on Gradescope looks like.</paragraph></list-item><list-item><paragraph>So if you pass 8/10 tests in your notebook, you should also pass the same 8/10 of the tests on Gradescope.</paragraph></list-item><list-item><paragraph>If you don't pass the same tests, make sure you are submitting to the right assignment and saving properly. If that still doesn't resolve your issue, please make an Ed post.</paragraph></list-item><list-item><paragraph>For labs, all the tests are public -- if you pass all of them, you will receive full credit. For homeworks and projects, some of the tests are private -- you are not guaranteed a full score even if you pass all the public tests (the ones you can see).</paragraph></list-item><list-item><paragraph>Please note that this video does NOT cover the submission of written work. You should follow the instructions written on each assignment to see how to submit written work.</paragraph></list-item></list><paragraph>Feel free to post any general questions in a follow-up below. Please <bold>make a private post</bold> (using the provided template under the "Lab" category) if you need help debugging or want to include anything with your code or solutions!</paragraph><paragraph>Have a gr8 day, and we look forward to seeing you in lab!</paragraph></document>"""

    @staticmethod
    def make_post(assignment_num, sandbox=False):
        params = {
            "type": "announcement",
            "title": f"Lab {int(assignment_num)} Released!",
            "category": "Lab",
            "subcategory": f"Lab {assignment_num}",
            "subsubcategory": None,
            "content": Lab.TEMPLATE.format(assignment_num),
            "is_pinned": False,
            "is_private": True,
            "is_anonymous": False,
            "is_megathread": True,
            "anonymous_comments": True
        }
        if sandbox:
            ID = SANDBOX
        else:
            ID = DATA8
        post_id = ed.post_thread(ID, params)["number"]
        print(f"Lab {assignment_num} post created with ID {post_id}")
