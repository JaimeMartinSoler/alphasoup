from page_alphasoup.alphasoup import AlphaSoup


class AlphaSoupBuilder:

    @staticmethod
    def build(config):
        return AlphaSoup(config['rows'], config['cols'], config['letters'], config['letters_weights_map'],
                         config['words'], config['ways'])
