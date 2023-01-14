import logging
import os
from pathlib import Path
import pdfkit

from utils.path_utils import get_fullpath_from_root

logger = logging.getLogger()


class PagePDFA5:

    def __init__(self, config_pdfa5, path_rel_html, path_rel_pdf):

        self.config_pdfa5 = config_pdfa5

        # path_rel
        self.path_rel_html = path_rel_html
        self.path_rel_pdf = path_rel_pdf

        # path
        self.path_html = get_fullpath_from_root(self.path_rel_html)
        self.path_pdf = get_fullpath_from_root(self.path_rel_pdf)

    def build_pdfa5(self):
        logger.info(f"build_pdfa5")
        self._make_dirs_output()
        self._run_pdfkit()

    def _make_dirs_output(self):
        os.makedirs(str(Path(self.path_pdf).parent), exist_ok=True)

    def _run_pdfkit(self):
        # https://apitemplate.io/blog/a-guide-to-generate-pdfs-in-python/
        pdfkit.from_file(self.path_html, self.path_pdf, options=self.config_pdfa5['options'])
