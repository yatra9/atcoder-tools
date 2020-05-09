import re

from bs4 import BeautifulSoup

TBODY_RE = re.compile(r'<tbody>.*</tbody>', re.DOTALL)
TR_RE = re.compile(r'<tr>.*?</tr>', re.DOTALL)
PROB_URL_RE = re.compile(
    r'"/tasks/([A-Za-z0-9\'~+\-_]+)"')
SUBMISSION_URL_RE = re.compile(
    r'"/submissions/([0-9]+)"')
RESULT_RE = re.compile(r'rel="tooltip".*?>(\w+)')


class Submission:

    def __init__(self, problem_id: str, submission_id: int, result: str):
        self.problem_id = problem_id
        self.submission_id = submission_id
        self.result = result

    @staticmethod
    def make_submissions_from(html: str):
        soup = BeautifulSoup(html, "html.parser")
        text = str(soup)
        m = TBODY_RE.search(text)
        if not m:
            return []
        text = TBODY_RE.search(text).group()

        def extract(elm):
            problem_id = PROB_URL_RE.search(elm).group(1)
            submission_id = SUBMISSION_URL_RE.search(elm).group(1)
            result = RESULT_RE.search(elm).group(1)
            return Submission(problem_id, int(submission_id), result)
        return [extract(elm) for elm in TR_RE.findall(text)]
