import re
from typing import Dict, Any, Optional, List

from atcodertools.codegen.code_style_config import CodeStyleConfig
from atcodertools.codegen.models.code_gen_args import CodeGenArgs
from atcodertools.codegen.template_engine import render
from atcodertools.fmtprediction.models.format import Pattern, SingularPattern, ParallelPattern, TwoDimensionalPattern, \
    Format
from atcodertools.fmtprediction.models.type import Type
from atcodertools.fmtprediction.models.variable import Variable
from atcodertools.client.models.problem import Problem
from atcodertools.client.models.sample import Sample


def _loop_header(var: Variable, for_second_index: bool):
    if for_second_index:
        index = var.second_index
        loop_var = "j"
    else:
        index = var.first_index
        loop_var = "i"
    lenstr = "{}".format(index.get_length())
    if not re.match(r'^\w+$', lenstr):
        lenstr = "({})".format(lenstr)
    return "for {loop_var} in 1:{lenstr}".format(
        loop_var=loop_var,
        lenstr=lenstr)


class JuliaCodeGenerator:

    def __init__(self,
                 format_: Optional[Format[Variable]],
                 config: CodeStyleConfig,
                 problem: Problem,
                 samples: List[Sample] = []):
        self._format = format_
        self._config = config
        self._problem = problem
        self._samples = samples

    def generate_parameters(self) -> Dict[str, Any]:
        submission_lang_pattern = self._config.lang.submission_lang_pattern
        langs = list(
            filter(lambda lang: submission_lang_pattern.match(lang), self._problem.langs))
        julia_version = ''
        if len(langs) >= 1:
            assert len(langs) == 1
            m = re.search(r'\((.*)\)', langs[0])
            if m:
                julia_version = m.group(1)

        if self._format is None:
            return dict(prediction_success=False,
                        indent=self._indent(1),
                        julia_version=julia_version,
                        samples=self._sample_part())

        return dict(formal_arguments=self._formal_arguments(),
                    actual_arguments=self._actual_arguments(),
                    input_part=self._input_part(),
                    prediction_success=True,
                    indent=self._indent(1),
                    julia_version=julia_version,
                    samples=self._sample_part())

    def _sample_part(self):
        def reshape(raw):
            return '"' + raw.strip().replace('\n', '\\n') + '"'
        return 'const samples = [' + ', '.join(['({}, {})'.format(reshape(s.get_input()), reshape(s.get_output())) for s in self._samples]) + ']'

    def _input_part(self):
        lines = []
        for pattern in self._format.sequence:
            lines += self._render_pattern(pattern)
        return "\n{indent}".format(indent=self._indent(1)).join(lines)

    def _convert_type(self, type_: Type) -> str:
        if type_ == Type.float:
            return "Float64"
        elif type_ == Type.int:
            return "Int"
        elif type_ == Type.str:
            return "String"
        else:
            raise NotImplementedError

    def _get_declaration_type(self, var: Variable):
        type = self._convert_type(var.type)
        if var.dim_num() == 0:
            return type
        elif var.dim_num() == 1:
            return "Vector{{{}}}".format(type)
        elif var.dim_num() == 2:
            return "Matrix{{{}}}".format(type)
        else:
            return "Array{{{t}, {nd}}}".format(t=type, nd=var.dim_num())

    def _actual_arguments(self) -> str:
        """
            :return the string form of actual arguments e.g. "N, K, a"
        """
        return ", ".join([
            v.name if v.dim_num() == 0 else '{}'.format(v.name)
            for v in self._format.all_vars()])

    def _formal_arguments(self):
        """
            :return the string form of formal arguments e.g. "int N, int K, std::vector<int> a"
        """
        return ", ".join([
            "{name}::{decl_type}".format(
                decl_type=self._get_declaration_type(v),
                name=v.name)
            for v in self._format.all_vars()
        ])

    def _generate_declaration(self, var: Variable):
        """
        :return: Create declaration part E.g. array[1..n] -> std::vector<int> array = std::vector<int>(n-1+1);
        """
        if var.dim_num() == 0:
            dims = []
        elif var.dim_num() == 1:
            dims = [var.first_index.get_length()]
        elif var.dim_num() == 2:
            dims = [var.first_index.get_length(),
                    var.second_index.get_length()]
        else:
            raise NotImplementedError

        t = self._convert_type(var.type)
        if len(dims) == 0:
            ret = ""
        else:
            d = []
            for dim in dims:
                d.append(str(dim))
            if len(dims) == 1:
                jtype = "Vector"
            elif len(dims) == 2:
                jtype = "Matrix"
            else:
                jtype = "Array"
            ret = "{name} = similar({jtype}{{{type}}}, {dims})".format(
                type=t, name=var.name, jtype=jtype, dims=", ".join(d))
        return ret

    def _input_code_for_var(self, var: Variable) -> str:
        name = self._get_var_name(var)
        if var.type == Type.float:
            return '{name} = parse(Float64, take!(tokens))'.format(name=name)
        elif var.type == Type.int:
            return '{name} = parse(Int, take!(tokens))'.format(name=name)
        elif var.type == Type.str:
            return '{name} = take!(tokens)'.format(name=name)
        else:
            raise NotImplementedError

    @staticmethod
    def _get_var_name(var: Variable):
        name = var.name
        if var.dim_num() >= 1:
            name += "[i"
            if var.dim_num() >= 2:
                name += ",j"
            name += "]"
        return name

    def _render_pattern(self, pattern: Pattern):
        lines = []
        for var in pattern.all_vars():
            line = self._generate_declaration(var)
            if len(line) > 0:
                lines.append(line)

        representative_var = pattern.all_vars()[0]
        if isinstance(pattern, SingularPattern):
            lines.append(self._input_code_for_var(representative_var))
        elif isinstance(pattern, ParallelPattern):
            lines.append(_loop_header(representative_var, False))
            for var in pattern.all_vars():
                lines.append("{indent}{line}".format(indent=self._indent(1),
                                                     line=self._input_code_for_var(var)))
            lines.append("end")
        elif isinstance(pattern, TwoDimensionalPattern):
            lines.append(_loop_header(representative_var, False))
            lines.append(
                "{indent}{line}".format(indent=self._indent(1), line=_loop_header(representative_var, True)))
            for var in pattern.all_vars():
                lines.append("{indent}{line}".format(indent=self._indent(2),
                                                     line=self._input_code_for_var(var)))
            lines.append("{indent}end".format(indent=self._indent(1)))
            lines.append("end")
        else:
            raise NotImplementedError

        return lines

    def _indent(self, depth):
        return self._config.indent(depth)


class NoPredictionResultGiven(Exception):
    pass


def main(args: CodeGenArgs) -> str:
    code_parameters = JuliaCodeGenerator(
        args.format, args.config, problem=args.problem, samples=args.samples).generate_parameters()
    return render(
        args.template,
        mod=args.constants.mod,
        yes_str=args.constants.yes_str,
        no_str=args.constants.no_str,
        contest_id=args.problem.contest.get_id(),
        problem_id=args.problem.problem_id,
        problem_alphabet=args.problem.alphabet,
        **code_parameters
    )
