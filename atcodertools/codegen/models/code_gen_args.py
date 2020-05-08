from typing import Optional, List

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.constprediction.models.problem_constant_set import ProblemConstantSet
from atcodertools.fmtprediction.models.format import Format
from atcodertools.fmtprediction.models.variable import Variable
from atcodertools.client.models.sample import Sample

class CodeGenArgs:

    def __init__(self,
                 template: str,
                 format_: Optional[Format[Variable]],
                 constants: ProblemConstantSet,
                 config: CodeStyleConfig,
                 samples: List[Sample] = []):
        self.template = template
        self.format = format_
        self.constants = constants
        self.config = config
        self.samples = samples
