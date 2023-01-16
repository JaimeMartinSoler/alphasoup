import copy
import shutil
from subprocess import call

from page_alphasoup.alphasoup_builder import AlphaSoupBuilder
from page_html.page_html import PageHTML
from page_pdf.page_pdf_merger import PagePDFmerger
from page_pdf.page_pdfa4 import PagePDFA4
from page_pdf.page_pdfa5 import PagePDFA5
from utils.config_loader import CONFIG
from utils.path_utils import get_fullpath_from_root


class PageGenerator:

    HTML_FILENAME_OUTPUT = 'page.html'

    def __init__(self, dir_rel, dir_rel_solution,
                 subdir_pages_html,
                 subdir_pages_pdfa5, subdir_pages_pdfa5_merger,
                 subdir_pages_pdfa4, subdir_pages_pdfa4_merger,
                 solution, html, pdfa5, pdfa5_merger, pdfa4, pdfa4_merger):

        # paths_rel
        self.dir_rel_output_pages = dir_rel
        self.dir_rel_pages_html = f'{self.dir_rel_output_pages}/{subdir_pages_html}'
        self.dir_rel_pages_pdfa5 = f'{self.dir_rel_output_pages}/{subdir_pages_pdfa5}'
        self.dir_rel_pages_pdfa5_merger = f'{self.dir_rel_output_pages}/{subdir_pages_pdfa5_merger}'
        self.dir_rel_pages_pdfa4 = f'{self.dir_rel_output_pages}/{subdir_pages_pdfa4}'
        self.dir_rel_pages_pdfa4_merger = f'{self.dir_rel_output_pages}/{subdir_pages_pdfa4_merger}'
        # paths_rel solution
        self.dir_rel_output_pages_solution = dir_rel_solution
        self.dir_rel_pages_html_solution = f'{self.dir_rel_output_pages_solution}/{subdir_pages_html}'
        self.dir_rel_pages_pdfa5_solution = f'{self.dir_rel_output_pages_solution}/{subdir_pages_pdfa5}'
        self.dir_rel_pages_pdfa5_merger_solution = f'{self.dir_rel_output_pages_solution}/{subdir_pages_pdfa5_merger}'
        self.dir_rel_pages_pdfa4_solution = f'{self.dir_rel_output_pages_solution}/{subdir_pages_pdfa4}'
        self.dir_rel_pages_pdfa4_merger_solution = f'{self.dir_rel_output_pages_solution}/{subdir_pages_pdfa4_merger}'

        # paths
        self.dir_output_pages = get_fullpath_from_root(self.dir_rel_output_pages)
        self.dir_pages_html = get_fullpath_from_root(self.dir_rel_pages_html)
        self.dir_pages_pdfa5 = get_fullpath_from_root(self.dir_rel_pages_pdfa5)
        self.dir_pages_pdfa5_merger = get_fullpath_from_root(self.dir_rel_pages_pdfa5_merger)
        self.dir_pages_pdfa4 = get_fullpath_from_root(self.dir_rel_pages_pdfa4)
        self.dir_pages_pdfa4_merger = get_fullpath_from_root(self.dir_rel_pages_pdfa4_merger)
        # paths solution
        self.dir_output_pages_solution = get_fullpath_from_root(self.dir_rel_output_pages_solution)
        self.dir_pages_html_solution = get_fullpath_from_root(self.dir_rel_pages_html_solution)
        self.dir_pages_pdfa5_solution = get_fullpath_from_root(self.dir_rel_pages_pdfa5_solution)
        self.dir_pages_pdfa5_merger_solution = get_fullpath_from_root(self.dir_rel_pages_pdfa5_merger_solution)
        self.dir_pages_pdfa4_solution = get_fullpath_from_root(self.dir_rel_pages_pdfa4_solution)
        self.dir_pages_pdfa4_merger_solution = get_fullpath_from_root(self.dir_rel_pages_pdfa4_merger_solution)

        # settings
        self.solution = solution
        self.html = html
        self.pdfa5 = pdfa5
        self.pdfa5_merger = pdfa5_merger
        self.pdfa4 = pdfa4
        self.pdfa4_merger = pdfa4_merger

    def generate_pages(self):

        # clear_output
        self.clear_output()

        # alphasoup, html, pdfa5 (minimum, mandatory)
        alphasoup_list, alphasoup_solution_list =\
            self.generate_alphasoup_list()
        path_rel_html_list, path_rel_html_solution_list =\
            self.generate_pages_html(alphasoup_list, alphasoup_solution_list)
        path_rel_pdfa5_list, path_rel_pdfa5_solution_list =\
            self.generate_pages_pdfa5(path_rel_html_list, path_rel_html_solution_list)

        # pdfa5_blank_for_pdfa4
        if self.pdfa4 or self.pdfa4_merger:
            path_rel_pdfa5_list, path_rel_pdfa5_solution_list =\
                self.generate_pages_pdfa5_blank_for_pdfa4( path_rel_pdfa5_list, path_rel_pdfa5_solution_list)

        # pdfa5_merger
        if self.pdfa5_merger:
            self.generate_pages_pdfa5_merger(path_rel_pdfa5_list, path_rel_pdfa5_solution_list)

        # pdfa4
        if self.pdfa4 or self.pdfa4_merger:
            path_rel_pdfa4_list, path_rel_pdfa4_solution_list = \
                self.generate_pages_pdfa4(path_rel_pdfa5_list, path_rel_pdfa5_solution_list)

            # pdfa4_merger
            if self.pdfa4_merger:
                self.generate_pages_pdfa4_merger(path_rel_pdfa4_list, path_rel_pdfa4_solution_list)

        # clean_output
        self.clean_output()

    def clear_output(self):
        """
        remove all output
        """
        shutil.rmtree(self.dir_output_pages, ignore_errors=True)
        shutil.rmtree(self.dir_output_pages_solution, ignore_errors=True)

    def clean_output(self):
        """
        remove undesired output subdirs, leave only the desired ones
        """
        if not self.html:
            shutil.rmtree(self.dir_pages_html, ignore_errors=True)
            shutil.rmtree(self.dir_pages_html_solution, ignore_errors=True)
        if not self.pdfa5:
            shutil.rmtree(self.dir_pages_pdfa5, ignore_errors=True)
            shutil.rmtree(self.dir_pages_pdfa5_solution, ignore_errors=True)
        if not self.pdfa5_merger:
            shutil.rmtree(self.dir_pages_pdfa5_merger, ignore_errors=True)
            shutil.rmtree(self.dir_pages_pdfa5_merger_solution, ignore_errors=True)
        if not self.pdfa4:
            shutil.rmtree(self.dir_pages_pdfa4, ignore_errors=True)
            shutil.rmtree(self.dir_pages_pdfa4_solution, ignore_errors=True)
        if not self.pdfa4_merger:
            shutil.rmtree(self.dir_pages_pdfa4_merger, ignore_errors=True)
            shutil.rmtree(self.dir_pages_pdfa4_merger_solution, ignore_errors=True)

    def generate_alphasoup_list(self):

        alphasoup_list = []
        alphasoup_solution_list = []

        for page in CONFIG['pages']:

            config_alphasoup = page['alphasoup']
            alphasoup = AlphaSoupBuilder.build(config_alphasoup)
            alphasoup.build_alphasoup(only_solution=True)
            if self.solution:
                alphasoup_solution = copy.deepcopy(alphasoup)
                alphasoup_solution_list.append(alphasoup_solution)
            alphasoup.build_soup_background()
            alphasoup_list.append(alphasoup)

        return alphasoup_list, alphasoup_solution_list

    def generate_pages_html(self, alphasoup_list, alphasoup_solution_list=None):

        path_rel_html_list = []
        path_rel_html_solution_list = []

        for i, page in enumerate(CONFIG['pages']):
            page_idx = i + 1
            page_idx_str = str(page_idx).zfill(3)

            # pages html
            alphasoup = alphasoup_list[i]
            config_html = page['html']
            dir_rel_page_input = 'templates/page'
            dir_rel_common_input = 'templates/common'
            dir_rel_page_output = f'{self.dir_rel_pages_html}/page{page_idx_str}'
            dir_rel_common_output = f'{self.dir_rel_pages_html}/common'
            page_html = PageHTML(alphasoup, config_html, page_idx,
                                 dir_rel_page_input, dir_rel_common_input,
                                 dir_rel_page_output, dir_rel_common_output, PageGenerator.HTML_FILENAME_OUTPUT)
            path_rel_html = page_html.build_page_html()
            path_rel_html_list.append(path_rel_html)

            # pages html solution
            if self.solution:
                alphasoup_solution = alphasoup_solution_list[i]
                dir_rel_page_output_solution = f'{self.dir_rel_pages_html_solution}/page{page_idx_str}'
                dir_rel_common_output_solution = f'{self.dir_rel_pages_html_solution}/common'
                page_html_solution = PageHTML(alphasoup_solution, config_html, page_idx,
                                              dir_rel_page_input, dir_rel_common_input,
                                              dir_rel_page_output_solution, dir_rel_common_output_solution,
                                              PageGenerator.HTML_FILENAME_OUTPUT)
                path_rel_html_solution = page_html_solution.build_page_html()
                path_rel_html_solution_list.append(path_rel_html_solution)

        return path_rel_html_list, path_rel_html_solution_list

    def generate_pages_pdfa5(self, path_rel_html_list, path_rel_html_solution_list=None):

        path_rel_pdfa5_list = []
        path_rel_pdfa5_solution_list = []

        for i, page in enumerate(CONFIG['pages']):
            page_idx = i + 1
            page_idx_str = str(page_idx).zfill(3)

            # pdfa5
            path_rel_html = path_rel_html_list[i]
            config_pdfa5 = page['pdfa5']
            path_rel_pdfa5 = f'{self.dir_rel_pages_pdfa5}/a5_{page_idx_str}.pdf'
            path_rel_pdfa5_list.append(path_rel_pdfa5)
            page_pdfa5 = PagePDFA5(config_pdfa5, path_rel_html, path_rel_pdfa5)
            page_pdfa5.build_pdfa5()

            # pdfa5_solution
            if self.solution:
                path_rel_html_solution = path_rel_html_solution_list[i]
                path_rel_pdfa5_solution = f'{self.dir_rel_pages_pdfa5_solution}/a5_{page_idx_str}.pdf'
                path_rel_pdfa5_solution_list.append(path_rel_pdfa5_solution)
                page_pdfa5_solution = PagePDFA5(config_pdfa5, path_rel_html_solution, path_rel_pdfa5_solution)
                page_pdfa5_solution.build_pdfa5()

        return path_rel_pdfa5_list, path_rel_pdfa5_solution_list

    def generate_pages_pdfa5_blank_for_pdfa4(self, path_rel_pdfa5_list, path_rel_pdfa5_solution_list=None):

        # add A5 blank_pages (divisible by 4, so that A4 (double A5) by both sides fits)
        if self.solution and len(path_rel_pdfa5_list) != len(path_rel_pdfa5_solution_list):
            raise RuntimeError(f"len(path_rel_pdfa5_list)={len(path_rel_pdfa5_list)}"
                               f" != len(path_rel_pdfa5_solution_list)={len(path_rel_pdfa5_solution_list)}")

        blank_pages = len(path_rel_pdfa5_list) % 4
        for i in range(len(path_rel_pdfa5_list), len(path_rel_pdfa5_list) + blank_pages):
            page_idx = i + 1
            page_idx_str = str(page_idx).zfill(3)

            # pdfa5
            path_rel_pdfa5 = f'{self.dir_rel_pages_pdfa5}/a5_{page_idx_str}.pdf'
            path_rel_pdfa5_list.append(path_rel_pdfa5)
            path_pdfa5 = get_fullpath_from_root(path_rel_pdfa5)
            script = f"convert xc:none -page A5 {path_pdfa5}"
            call(script, shell=True)

            # pdfa5_solution
            if self.solution:
                path_rel_pdfa5_solution = f'{self.dir_rel_pages_pdfa5_solution}/a5_{page_idx_str}.pdf'
                path_rel_pdfa5_solution_list.append(path_rel_pdfa5_solution)
                path_pdfa5_solution = get_fullpath_from_root(path_rel_pdfa5_solution)
                script_solution = f"convert xc:none -page A5 {path_pdfa5_solution}"
                call(script_solution, shell=True)

        return path_rel_pdfa5_list, path_rel_pdfa5_solution_list

    def generate_pages_pdfa5_merger(self, path_rel_pdfa5_list, path_rel_pdfa5_solution_list=None):

        # pdfa5_merger
        filename_output = f'alphasoup_a5.pdf'
        page_pdfa5_merger = PagePDFmerger(path_rel_pdfa5_list, self.dir_rel_pages_pdfa5_merger, filename_output)
        page_pdfa5_merger.build_pdf_merger()

        # pdfa5_merger_solution
        if self.solution:
            filename_output_solution = f'alphasoup_a5_solution.pdf'
            page_pdfa5_merger_solution = PagePDFmerger(path_rel_pdfa5_solution_list,
                                                       self.dir_rel_pages_pdfa5_merger_solution,
                                                       filename_output_solution)
            page_pdfa5_merger_solution.build_pdf_merger()

    def generate_pages_pdfa4(self, path_rel_pdfa5_list, path_rel_pdfa5_solution_list=None):

        # pdfa4
        path_rel_pdfa4_list = PageGenerator._build_all_pdfa4_from_pdfa5(
            path_rel_pdfa5_list, self.dir_rel_pages_pdfa4)

        # pdfa4_solution
        if self.solution:
            path_rel_pdfa4_solution_list = PageGenerator._build_all_pdfa4_from_pdfa5(
                path_rel_pdfa5_solution_list, self.dir_rel_pages_pdfa4_solution)
        else:
            path_rel_pdfa4_solution_list = None

        return path_rel_pdfa4_list, path_rel_pdfa4_solution_list

    def generate_pages_pdfa4_merger(self, path_rel_pdfa4_list, path_rel_pdfa4_solution_list=None):

        # pdfa4_merger
        filename_output = f'alphasoup_a4.pdf'
        page_pdfa4_merger = PagePDFmerger(path_rel_pdfa4_list, self.dir_rel_pages_pdfa4_merger, filename_output)
        page_pdfa4_merger.build_pdf_merger()

        # pdfa4_merger_solution
        if self.solution:
            filename_output_solution = f'alphasoup_a4_solution.pdf'
            page_pdfa4_merger_solution = PagePDFmerger(path_rel_pdfa4_solution_list,
                                                       self.dir_rel_pages_pdfa4_merger_solution,
                                                       filename_output_solution)
            page_pdfa4_merger_solution.build_pdf_merger()

    @staticmethod
    def _build_all_pdfa4_from_pdfa5(path_rel_pdfa5_list, dir_rel_pdfa4):

        path_rel_pdfa4_list = []
        pdfa4_pages = int((len(path_rel_pdfa5_list) + 1) / 2)  # = ceil(len(path_rel_pdfa5_list)/2)

        for i in range(pdfa4_pages):
            page_idx = i + 1
            page_idx_str = str(page_idx).zfill(3)
            filename_output = f'a4_{page_idx_str}.pdf'

            # even
            if i % 2 == 0:
                path_rel_pdfa5_left = path_rel_pdfa5_list[-(1+i)]
                path_rel_pdfa5_right = path_rel_pdfa5_list[i]
                flip = False
            # odd
            else:
                path_rel_pdfa5_left = path_rel_pdfa5_list[i]
                path_rel_pdfa5_right = path_rel_pdfa5_list[-(1+i)]
                flip = True

            # PagePDFA4
            page_pdfa4 = PagePDFA4(path_rel_pdfa5_left, path_rel_pdfa5_right, dir_rel_pdfa4, filename_output, flip)
            page_pdfa4.build_pdfa4()
            path_rel_pdfa4_list.append(page_pdfa4.path_rel_pdfa4)

        return path_rel_pdfa4_list
