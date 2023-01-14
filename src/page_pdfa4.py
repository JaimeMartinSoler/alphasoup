import logging
import os
from subprocess import call

from utils.path_utils import get_fullpath_from_root

logger = logging.getLogger()


class PagePDFA4:

    def __init__(self, path_rel_pdfa5_left, path_rel_pdfa5_right, dir_rel_pdfa4, filename_output, flip=False):

        # path_rel, dir_rel
        self.path_rel_pdfa5_left = path_rel_pdfa5_left
        self.path_rel_pdfa5_right = path_rel_pdfa5_right
        self.dir_rel_pdfa4 = dir_rel_pdfa4
        self.filename_output = filename_output
        self.flip = flip
        self.path_rel_pdfa4 = f'{self.dir_rel_pdfa4}{os.sep}{self.filename_output}'

        # path, dir
        self.path_pdfa5_left = get_fullpath_from_root(self.path_rel_pdfa5_left)
        self.path_pdfa5_right = get_fullpath_from_root(self.path_rel_pdfa5_right)
        self.dir_pdfa4 = get_fullpath_from_root(self.dir_rel_pdfa4)
        self.path_pdfa4 = get_fullpath_from_root(self.path_rel_pdfa4)

    def build_pdfa4(self):
        logger.info(f"build_pdfa4")
        self._make_dirs_output()
        self._run_script()

    def _make_dirs_output(self):
        os.makedirs(self.dir_pdfa4, exist_ok=True)

    def _run_script(self):
        pdftk_param_flip = 'endsouth' if self.flip else 'endnorth'
        script = f"""
            pdftk A={self.path_pdfa5_left} B={self.path_pdfa5_right} cat A1 B1 output - \
            | pdf2ps -dLanguageLevel=3 - - \
            | psnup -2 -Pa5 -pa4 \
            | ps2pdf -dCompatibility=1.4 - - \
            | pdftk - cat 1-{pdftk_param_flip} output {self.path_pdfa4}
        """
        call(script, shell=True)
