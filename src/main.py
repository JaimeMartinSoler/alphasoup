import copy
import logging
import shutil
from subprocess import call

from alphasoup import AlphaSoupBuilder
from page_html import PageHTML
from page_pdf_merger import PagePDFmerger
from page_pdfa5 import PagePDFA5
from page_pdfa4 import PagePDFA4
from utils.config_loader import CONFIG
from utils.logger_builder import build_logger
from utils.path_utils import get_fullpath_from_root


def main():

    path_rel_pdfa5_list = []
    path_rel_pdfa5_solution_list = []

    # clear output
    path_rel_output_pages = f'output/pages'
    path_output_pages = get_fullpath_from_root(path_rel_output_pages)
    shutil.rmtree(path_output_pages, ignore_errors=True)
    # clear output solution
    path_rel_output_pages_solution = f'output/pages_solution'
    path_output_pages_solution = get_fullpath_from_root(path_rel_output_pages_solution)
    shutil.rmtree(path_output_pages_solution, ignore_errors=True)

    for i, page in enumerate(CONFIG['pages']):
        page_idx = i + 1
        page_idx_str = str(page_idx).zfill(3)

        # alphasoup, alphasoup_solution
        config_alphasoup = page['alphasoup']
        alphasoup = AlphaSoupBuilder.build(config_alphasoup)
        alphasoup.build_alphasoup(only_solution=True)
        # alphasoup_solution
        alphasoup_solution = copy.deepcopy(alphasoup)
        alphasoup.build_soup_background()

        # html
        config_html = page['html']
        dir_rel_page_input = 'templates/page'
        dir_rel_common_input = 'templates/common'
        dir_rel_page_output = f'{path_rel_output_pages}/pages_html/page{page_idx_str}'
        dir_rel_common_output = f'{path_rel_output_pages}/pages_html/common'
        html_filename_output = 'page.html'
        page_html = PageHTML(alphasoup, config_html, page_idx,
                             dir_rel_page_input, dir_rel_common_input,
                             dir_rel_page_output, dir_rel_common_output, html_filename_output)
        page_html.build_page_html()
        # html_solution
        dir_rel_page_output_solution = f'{path_rel_output_pages_solution}/pages_html/page{str(page_idx).zfill(3)}'
        dir_rel_common_output_solution = f'{path_rel_output_pages_solution}/pages_html/common'
        page_html_solution = PageHTML(alphasoup_solution, config_html, page_idx,
                                      dir_rel_page_input, dir_rel_common_input,
                                      dir_rel_page_output_solution, dir_rel_common_output_solution, html_filename_output)
        page_html_solution.build_page_html()

        # pdfa5
        config_pdfa5 = page['pdfa5']
        path_rel_html = f'{dir_rel_page_output}/html/{html_filename_output}'
        path_rel_pdfa5 = f'{path_rel_output_pages}/pages_pdfa5/a5_{page_idx_str}.pdf'
        path_rel_pdfa5_list.append(path_rel_pdfa5)
        page_pdfa5 = PagePDFA5(config_pdfa5, path_rel_html, path_rel_pdfa5)
        page_pdfa5.build_pdfa5()
        # pdfa5_solution
        path_rel_html_solution = f'{dir_rel_page_output_solution}/html/{html_filename_output}'
        path_rel_pdfa5_solution = f'{path_rel_output_pages_solution}/pages_pdfa5/a5_{page_idx_str}.pdf'
        path_rel_pdfa5_solution_list.append(path_rel_pdfa5_solution)
        page_pdfa5_solution = PagePDFA5(config_pdfa5, path_rel_html_solution, path_rel_pdfa5_solution)
        page_pdfa5_solution.build_pdfa5()

    # add A5 blank_pages (divisible by 4, so that A4 (double A5) by both sides fits)
    if len(path_rel_pdfa5_list) != len(path_rel_pdfa5_solution_list):
        raise RuntimeError(f"len(path_rel_pdfa5_list)={len(path_rel_pdfa5_list)}"
                           f" != len(path_rel_pdfa5_solution_list)={len(path_rel_pdfa5_solution_list)}")
    blank_pages = len(path_rel_pdfa5_list) % 4
    for i in range(len(path_rel_pdfa5_list), len(path_rel_pdfa5_list) + blank_pages):
        page_idx = i + 1
        page_idx_str = str(page_idx).zfill(3)
        # pdfa5
        path_rel_pdfa5 = f'{path_rel_output_pages}/pages_pdfa5/a5_{page_idx_str}.pdf'
        path_rel_pdfa5_list.append(path_rel_pdfa5)
        path_pdfa5 = get_fullpath_from_root(path_rel_pdfa5)
        script = f"convert xc:none -page A5 {path_pdfa5}"
        call(script, shell=True)
        # pdfa5_solution
        path_rel_pdfa5_solution = f'{path_rel_output_pages_solution}/pages_pdfa5/a5_{page_idx_str}.pdf'
        path_rel_pdfa5_solution_list.append(path_rel_pdfa5_solution)
        path_pdfa5_solution = get_fullpath_from_root(path_rel_pdfa5_solution)
        script_solution = f"convert xc:none -page A5 {path_pdfa5_solution}"
        call(script_solution, shell=True)

    # pdfa5_merger
    dir_rel_pdfa5_merger = f'{path_rel_output_pages}/pages_pdfa5_merger'
    filename_output = f'alphasoup_a5.pdf'
    page_pdfa5_merger = PagePDFmerger(path_rel_pdfa5_list, dir_rel_pdfa5_merger, filename_output)
    page_pdfa5_merger.build_pdf_merger()
    # pdfa5_merger_solution
    dir_rel_pdfa5_merger_solution = f'{path_rel_output_pages_solution}/pages_pdfa5_merger'
    filename_output_solution = f'alphasoup_a5_solution.pdf'
    page_pdfa5_merger_solution = PagePDFmerger(path_rel_pdfa5_solution_list, dir_rel_pdfa5_merger_solution, filename_output_solution)
    page_pdfa5_merger_solution.build_pdf_merger()

    # pdfa4
    dir_rel_pdfa4 = f'{path_rel_output_pages}/pages_pdfa4'
    path_rel_pdfa4_list = build_all_pdfa4_from_pdfa5(path_rel_pdfa5_list, dir_rel_pdfa4)
    # pdfa4_solution
    dir_rel_pdfa4_solution = f'{path_rel_output_pages_solution}/pages_pdfa4'
    path_rel_pdfa4_solution_list = build_all_pdfa4_from_pdfa5(path_rel_pdfa5_solution_list, dir_rel_pdfa4_solution)

    # pdfa4_merger
    dir_rel_pdfa4_merger = f'{path_rel_output_pages}/pages_pdfa4_merger'
    filename_output = f'alphasoup_a4.pdf'
    page_pdfa4_merger = PagePDFmerger(path_rel_pdfa4_list, dir_rel_pdfa4_merger, filename_output)
    page_pdfa4_merger.build_pdf_merger()
    # pdfa4_merger_solution
    dir_rel_pdfa4_merger_solution = f'{path_rel_output_pages_solution}/pages_pdfa4_merger'
    filename_output_solution = f'alphasoup_a4_solution.pdf'
    page_pdfa4_merger_solution = PagePDFmerger(path_rel_pdfa4_solution_list, dir_rel_pdfa4_merger_solution, filename_output_solution)
    page_pdfa4_merger_solution.build_pdf_merger()


def build_all_pdfa4_from_pdfa5(path_rel_pdfa5_list, dir_rel_pdfa4):

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


if __name__ == '__main__':

    # logger
    build_logger(log_level=logging.DEBUG)

    # main()
    main()
