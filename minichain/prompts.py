from typing import Any, Mapping

from jinja2 import Environment, FileSystemLoader, Template

from .backend import Request
from .base import HTML, Output, Prompt


class SimplePrompt(Prompt[str, str]):
    """
    A simple prompt that echos the string it is passed and returns the
    output of the LLM as a string.
    """

    def prompt(self, inp: str) -> Request:
        return Request(inp)

    def parse(self, out: str, inp: str) -> str:
        return out


class JinjaPrompt(Prompt[Mapping[str, Any], Output]):
    """
    A prompt that uses Jinja2 to define a prompt based on a static template.
    """

    IN = Mapping[str, Any]
    template = None
    template_file = ""
    prompt_template = ""
    stop_template = ""

    def render_prompt_html(self, inp: Mapping[str, Any], prompt: str) -> HTML:
        n = {
            k: f"<div style='color:red'>{v}</div>" if isinstance(v, str) else v
            for k, v in inp.items()
        }
        return HTML(self.prompt(n).prompt.replace("\n", "<br>"))

    def parse(self, result: str, inp: Mapping[str, Any]) -> Output:
        return result

    def prompt(self, kwargs: Mapping[str, Any]) -> Request:
        if self.template_file:
            tmp = Environment(loader=FileSystemLoader(".")).get_template(
                name=self.template_file
            )
        elif self.template:
            tmp = self.template  # type: ignore
        else:
            tmp = Template(self.prompt_template)
        x = tmp.render(**kwargs)
        if self.stop_template:
            stop = [Template(self.stop_template).render(**kwargs)]
        else:
            stop = None
        return Request(x, stop)
