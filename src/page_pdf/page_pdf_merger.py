import logging
import os
from subprocess import call

from utils.path_utils import get_fullpath_from_root

logger = logging.getLogger()


class PagePDFmerger:

    def __init__(self, path_rel_pdf_list, dir_rel_pdf_merger, filename_output):

        # path_rel, dir_rel
        self.path_rel_pdf_list = path_rel_pdf_list
        self.dir_rel_pdf_merger = dir_rel_pdf_merger
        self.filename_output = filename_output
        self.path_rel_pdf_merger = f'{self.dir_rel_pdf_merger}/{self.filename_output}'

        # path, dir
        self.path_pdf_list = [get_fullpath_from_root(p) for p in self.path_rel_pdf_list]
        self.dir_pdf_merger = get_fullpath_from_root(self.dir_rel_pdf_merger)
        self.path_pdf_merger = get_fullpath_from_root(self.path_rel_pdf_merger)

    def build_pdf_merger(self):
        logger.info(f"build_pdf_merger")
        self._make_dirs_output()
        self._run_script()

    def _make_dirs_output(self):
        os.makedirs(self.dir_pdf_merger, exist_ok=True)

    def _run_script(self):
        script = f"""
            pdftk {' '.join(self.path_pdf_list)} cat output {self.path_pdf_merger}
        """
        call(script, shell=True)
