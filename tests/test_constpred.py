import logging
import os
import tempfile
import unittest
from typing import List
from unicodedata import east_asian_width

from bs4 import BeautifulSoup

from atcodertools.constprediction.constants_prediction import predict_constants, predict_modulo
from tests.utils.gzip_controller import make_html_data_controller

ANSWER_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    './resources/test_constpred/answer.txt')

fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmt)


def _to_str(x):
    if x is None:
        return ""
    return str(x)


def extract_context(text: str, kw: str, width=10) -> List[str]:
    pos = 0
    res = []
    while True:
        pos = text.find(kw, pos)
        if pos == -1:
            return res
        start = max(0, pos - width)
        end = min(pos + width, len(text))
        res.append(text[start:end])
        pos += 1


def length(s):
    len_ = 0
    for i in s:
        if 'NaH'.count(east_asian_width(i)) > 0:
            len_ += 1
        else:
            len_ += 2
    return len_


class TestConstantsPrediction(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.html_data_controller = make_html_data_controller(
            tempfile.mkdtemp())
        self.test_dir = self.html_data_controller.create_dir()

    def tearDown(self):
        self.html_data_controller.remove_dir()

    def test_predict_constants(self):
        # Test prediction with AGC data
        with open(ANSWER_FILE, 'r') as f:
            answers = f.read().split("\n")

        agc_html_paths = [path for path in sorted(
            os.listdir(self.test_dir)) if "agc" in path]
        for html_path, answer_line in zip(agc_html_paths, answers):
            logging.debug("Testing {}".format(html_path))
            constants = predict_constants(self._load(html_path))
            output_line = "{:40} [mod]{:10} [yes]{:10} [no]{:10}".format(html_path.split(".")[0],
                                                                         _to_str(
                                                                             constants.mod),
                                                                         _to_str(
                                                                             constants.yes_str),
                                                                         _to_str(constants.no_str))
            self.assertEqual(answer_line.rstrip(), output_line.rstrip())

    def _load(self, html_path):
        with open(os.path.join(self.test_dir, html_path), 'r') as f:
            return f.read()

    def test_recall_with_full_data(self):
        high_recall_kws = ["余", "余り", "あまり", "modulo", "mod", "10^9+7", "1000000007"]

        for html_path in sorted(os.listdir(self.test_dir)):
            html = self._load(html_path)
            html = BeautifulSoup(html, "html.parser").get_text()
            html = html.replace(",", "").replace("{", "").replace("}", "").replace(" ", "")
            detected_kws = [kw for kw in high_recall_kws if kw in html]
            if len(detected_kws) > 0:
                contexts = []
                for kw in detected_kws:
                    contexts += extract_context(html, kw)

                mod = predict_modulo(html)

                if mod is None:
                    print("{:40} {:15} {}".format(
                        html_path.split(".")[0],
                        _to_str(mod),
                        "".join(["\n{0}{1}".format(x, 80 - length(x)) for x in contexts])))
                    print("=============")
        pass


if __name__ == '__main__':
    unittest.main()
