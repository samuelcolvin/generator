"""
Taken approximately from https://github.com/tutorcruncher/pydf
"""
import subprocess
from tempfile import NamedTemporaryFile


def execute_wk(*args):
    """
    Generate path for the wkhtmltopdf binary and execute command.
    :param args: args to pass straight to subprocess.Popen
    :return: stdout, stderr
    """
    wk_args = ('wkhtmltopdf',) + args
    p = subprocess.Popen(wk_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout, stderr, p.returncode


def gen_pdf(src, cmd_args):
    with NamedTemporaryFile(suffix='.pdf', mode='rb+', delete=False) as pdf_file:
        cmd_args += [src, pdf_file.name]
        _, stderr, returncode = execute_wk(*cmd_args)
        pdf_file.seek(0)
        pdf_data = pdf_file.readline()
        # it seems wkhtmltopdf's error codes can be false, we'll ignore them if we
        # seem to have generated a pdf
        if returncode != 0 and pdf_data[:4] != b'%PDF':
            raise IOError('error running wkhtmltopdf, command: %r\nresponse: "%s"' % (cmd_args, stderr.strip()))
    return pdf_file.name


def generate_pdf(html,
                 quiet=True,
                 grayscale=False,
                 lowquality=False,
                 margin_bottom=None,
                 margin_left=None,
                 margin_right=None,
                 margin_top=None,
                 orientation=None,
                 page_height=None,
                 page_width=None,
                 page_size=None,
                 image_dpi=None,
                 image_quality=None,
                 **extra_kwargs):
    """
    Generate a pdf from either a url or a html string.
    After the html and url arguments all other arguments are
    passed straight to wkhtmltopdf
    For details on extra arguments see the output of get_help()
    and get_extended_help()
    All arguments whether specified or caught with extra_kwargs are converted
    to command line args with "'--' + original_name.replace('_', '-')"
    Arguments which are True are passed with no value eg. just --quiet, False
    and None arguments are missed, everything else is passed with str(value).
    :param html: html string to generate pdf from
    :param quiet: bool
    :param grayscale: bool
    :param lowquality: bool
    :param margin_bottom: string eg. 10mm
    :param margin_left: string eg. 10mm
    :param margin_right: string eg. 10mm
    :param margin_top: string eg. 10mm
    :param orientation: Portrait or Landscape
    :param page_height: string eg. 10mm
    :param page_width: string eg. 10mm
    :param page_size: string: A4, Letter, etc.
    :param image_dpi: int default 600
    :param image_quality: int default 94
    :param extra_kwargs: any exotic extra options for wkhtmltopdf
    :return: string representing pdf
    """
    loc = locals()
    py_args = {n: loc[n] for n in
               ['quiet', 'grayscale', 'lowquality', 'margin_bottom', 'margin_left', 'margin_right', 'margin_top',
               'orientation', 'page_height', 'page_width', 'page_size', 'image_dpi', 'image_quality']}
    py_args.update(extra_kwargs)
    cmd_args = []
    for name, value in py_args.items():
        if value in [None, False]:
            continue
        arg_name = '--' + name.replace('_', '-')
        if value is True:
            cmd_args.append(arg_name)
        else:
            cmd_args.extend([arg_name, str(value)])

    with NamedTemporaryFile(suffix='.html', mode='w') as html_file:
        html_file.write(html)
        html_file.flush()
        html_file.seek(0)
        return gen_pdf(html_file.name, cmd_args)
