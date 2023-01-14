import logging
import os
from pathlib import Path
import shutil

from utils.general_utils import split_list_in_chunks_equals
from utils.path_utils import get_fullpath_from_root

logger = logging.getLogger()


class PageHTML:

    # html text
    TAG_TITLE = '__TAG_TITLE__'
    TAG_DESCRIPTION = '__TAG_DESCRIPTION__'
    TAG_WAYS_ALLOWED_TEXT = '__TAG_WAYS_ALLOWED_TEXT__'
    TAG_WAYS_ALLOWED_IMGS = '__TAG_WAYS_ALLOWED_IMGS__'
    TAG_PAGE_IDX = '__TAG_PAGE_IDX__'

    # html tables
    TAG_TBODY_SOUP = '__TAG_TBODY_SOUP__'
    TAG_TBODY_WORDS = '__TAG_TBODY_WORDS__'
    TAG_TD_SOUP_FONT_SIZE_PX = '__TAG_TD_SOUP_FONT_SIZE_PX__'
    TAG_TD_WORD_FONT_SIZE_PX = '__TAG_TD_WORD_FONT_SIZE_PX__'

    # css
    TAG_TD_WORD_COLUMN_CONTAINER_WIDTH = '__TAG_TD_WORD_COLUMN_CONTAINER_WIDTH__'
    TAG_TABLE_SOUP_HEIGHT = '__TAG_TABLE_SOUP_HEIGHT__'
    TAG_TABLE_SOUP_WIDTH = '__TAG_TABLE_SOUP_WIDTH__'

    # validate
    ALPHASOUP_ROWS_MAX = 24
    ALPHASOUP_COLS_MAX = 24
    ALPHASOUP_WORDS_MAX = 32

    # config
    TD_SOUP_FONT_SIZE_FACTOR_DEFAULT = 1.0

    def __init__(self, alphasoup, config_html, page_idx,
                 dir_rel_page_input, dir_rel_common_input,
                 dir_rel_page_output, dir_rel_common_output, html_filename_output):

        self.alphasoup = alphasoup
        self.page_idx = page_idx
        self.config_html = config_html

        # config_html
        self.title = self.config_html['title']
        self.description = self.config_html['description']
        self.ways_allowed_text = self.config_html['ways_allowed_text']
        self.word_cols = self.config_html['word_cols']
        self.word_per_col_max = self.config_html['word_per_col_max']
        self.word_checkers = self.config_html['word_checkers']
        self.table_soup_px_max = self.config_html['table_soup_px_max']
        self.px_per_cell = self.config_html['px_per_cell']
        self.td_soup_font_size_px = self.config_html['td_soup_font_size_px']
        self.td_word_font_size_px = self.config_html['td_word_font_size_px']
        self.td_soup_font_size_factor = PageHTML.TD_SOUP_FONT_SIZE_FACTOR_DEFAULT
        self.build_config_params()

        # dir_rel
        self.dir_rel_page_input = dir_rel_page_input
        self.dir_rel_common_input = dir_rel_common_input
        self.dir_rel_page_output = dir_rel_page_output
        self.dir_rel_common_output = dir_rel_common_output
        self.html_filename_output = html_filename_output

        # path (full)
        self.dir_page_input = get_fullpath_from_root(dir_rel_page_input)
        self.dir_common_input = get_fullpath_from_root(dir_rel_common_input)
        self.dir_page_output = get_fullpath_from_root(dir_rel_page_output)
        self.path_html_output = f"{self.dir_page_output}{os.sep}html{os.sep}{self.html_filename_output}"
        self.path_css_output = f"{self.dir_page_output}{os.sep}html{os.sep}styles.css"
        self.dir_common_output = get_fullpath_from_root(dir_rel_common_output)

        # validate
        self._validate()

    def build_page_html(self):
        logger.info(f"build_page_html, for page_idx={self.page_idx}")
        self._copy_files()
        self._build_and_replace_output_html()
        self._build_and_replace_output_css()

    def _validate(self):
        if self.alphasoup.rows > PageHTML.ALPHASOUP_ROWS_MAX:
            raise ValueError(f"alphasoup.rows={self.alphasoup.rows} > ALPHASOUP_ROWS_MAX={PageHTML.ALPHASOUP_ROWS_MAX}")
        if self.alphasoup.cols > PageHTML.ALPHASOUP_COLS_MAX:
            raise ValueError(f"alphasoup.cols={self.alphasoup.cols} > ALPHASOUP_COLS_MAX={PageHTML.ALPHASOUP_COLS_MAX}")
        if len(self.alphasoup.words) > PageHTML.ALPHASOUP_WORDS_MAX:
            raise ValueError(f"alphasoup.words={len(self.alphasoup.words)} > ALPHASOUP_WORDS_MAX={PageHTML.ALPHASOUP_WORDS_MAX}")
        return True

    def build_config_params(self):

        # config_html
        self.title = self.config_html['title']
        self.description = self.config_html['description']
        self.ways_allowed_text = self.config_html['ways_allowed_text']
        self.word_cols = self.config_html['word_cols']
        self.word_per_col_max = self.config_html['word_per_col_max']
        self.word_checkers = self.config_html['word_checkers']
        self.table_soup_px_max = self.config_html['table_soup_px_max']
        self.px_per_cell = self.config_html['px_per_cell']
        self.td_soup_font_size_px = self.config_html['td_soup_font_size_px']
        self.td_word_font_size_px = self.config_html['td_word_font_size_px']
        self.td_soup_font_size_factor = PageHTML.TD_SOUP_FONT_SIZE_FACTOR_DEFAULT

        # word_cols, word_per_col_max
        if not isinstance(self.word_cols, int) or self.word_cols <= 0:
            self.word_cols = int((len(self.alphasoup.words) - 1) / self.word_per_col_max) + 1

        # td_soup_font_size_factor, td_soup_font_size_px, px_per_cell
        rc_max = max(self.alphasoup.rows, self.alphasoup.cols)
        side_max = self.px_per_cell * rc_max
        self.td_soup_font_size_factor = self.table_soup_px_max / side_max\
            if side_max > self.table_soup_px_max else 1.0
        if self.td_soup_font_size_factor < 1.0:
            self.px_per_cell *= self.td_soup_font_size_factor
            self.td_soup_font_size_px *= self.td_soup_font_size_factor

        # td_word_font_size_px
        if self.word_cols == 3:
            self.td_word_font_size_px -= 2
        elif self.word_cols >= 4:
            self.td_word_font_size_px -= 4

    def _build_and_replace_output_html(self):

        div_ways_imgs = self._get_div_ways_imgs()
        tbody_words = self._get_tbody_words()
        tbody_soup = self._get_tbody_soup()
        p_page_idx = self._get_p_page_idx()

        # open path_html_output
        f = open(self.path_html_output, 'r+')
        f_content = f.read()
        # replace
        f_content = f_content.replace(PageHTML.TAG_WAYS_ALLOWED_IMGS, div_ways_imgs)
        f_content = f_content.replace(PageHTML.TAG_TITLE, self.title)
        f_content = f_content.replace(PageHTML.TAG_DESCRIPTION, self.description)
        f_content = f_content.replace(PageHTML.TAG_WAYS_ALLOWED_TEXT, self.ways_allowed_text)
        f_content = f_content.replace(PageHTML.TAG_PAGE_IDX, p_page_idx)
        f_content = f_content.replace(PageHTML.TAG_TBODY_WORDS, tbody_words)
        f_content = f_content.replace(PageHTML.TAG_TBODY_SOUP, tbody_soup)
        # save
        f.seek(0)
        f.truncate()
        f.write(f_content)
        f.close()

    def _build_and_replace_output_css(self):

        td_word_column_container_width = str(100.0 / self.word_cols)[:5]
        table_soup_height = str(self.px_per_cell * self.alphasoup.rows)
        table_soup_width = str(self.px_per_cell * self.alphasoup.cols)
        td_soup_font_size_px = str(self.td_soup_font_size_px)
        td_word_font_size_px = str(self.td_word_font_size_px)

        # open path_css_output
        f = open(self.path_css_output, 'r+')
        f_content = f.read()
        # replace
        f_content = f_content.replace(PageHTML.TAG_TD_WORD_COLUMN_CONTAINER_WIDTH, td_word_column_container_width)
        f_content = f_content.replace(PageHTML.TAG_TABLE_SOUP_HEIGHT, table_soup_height)
        f_content = f_content.replace(PageHTML.TAG_TABLE_SOUP_WIDTH, table_soup_width)
        f_content = f_content.replace(PageHTML.TAG_TD_SOUP_FONT_SIZE_PX, td_soup_font_size_px)
        f_content = f_content.replace(PageHTML.TAG_TD_WORD_FONT_SIZE_PX, td_word_font_size_px)
        # save
        f.seek(0)
        f.truncate()
        f.write(f_content)
        f.close()

    def _copy_files(self):
        shutil.copytree(self.dir_page_input, self.dir_page_output, dirs_exist_ok=True)
        shutil.copytree(self.dir_common_input, self.dir_common_output, dirs_exist_ok=True)

    def _get_div_ways_imgs(self):
        div_ways = ''
        for way in self.alphasoup.ways:
            p_way = f"""
                    <p><img src="../../common/img/way_{way}.png"/></p>"""
            div_ways += p_way
        return div_ways

    def _get_p_page_idx(self):
        p_page_idx = f"    <p>- {self.page_idx} -</p>"
        return p_page_idx

    def _get_tbody_words(self):

        table_word_checker_unit = """
                                        <td class="td-word_checker"></td>"""
        table_word_checker = f"""
                                <table class="table-word_checker">
                                    <tbody>
                                    <tr>
                                        {''.join([table_word_checker_unit for _ in range(self.word_checkers)])}
                                    </tr>
                                    </tbody>
                                </table>
        """

        tbody = """
            <tr>
        """

        word_list_chunks = split_list_in_chunks_equals(self.alphasoup.words, self.word_cols)
        logger.info(f"word_list_chunks: {word_list_chunks}")

        # tbody_word
        tbody_word_chunks = []
        for w_list in word_list_chunks:
            tbody_word = ''
            for word in w_list:
                tr_word = f"""
                            <tr>
                                <td class="td-word_checker_container">
                                    {table_word_checker}
                                </td>
                                <td class="td-word">{word}</td>
                            </tr>
                """
                tbody_word += tr_word
            tbody_word_chunks.append(tbody_word)

        for tbody_word in tbody_word_chunks:
            tbody_col = f"""
                <td class="td-word_column_container">
                    <table class="table-word_column_container">
                        <tbody>
                        {tbody_word}
                        </tbody>
                    </table>
                </td>
            """
            tbody += tbody_col
        tbody += """
            </tr>
        """
        return tbody

    def _get_tbody_soup(self):
        tbody = ''
        for row in range(self.alphasoup.rows):
            tr_open = f'\n<tr class="tr-soup">'
            tbody += tr_open
            for col in range(self.alphasoup.cols):
                td = f'\n<td class="td-soup">{self.alphasoup.soup[row][col]}</td>'
                tbody += td
            tr_close = f'\n</tr>'
            tbody += tr_close
        return tbody

