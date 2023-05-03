import re

TAG = '[flounder]'
LINK = '-->'
DOT_LINK = '..>'
END_OF_CLASS = '%%END OF CLASS'
END_OF_LINK = '%%END OF LINK'
INITIAL_TEMPLATE = f'```mermaid\n\n{END_OF_CLASS}\n\n{END_OF_LINK}```'

class Flounder:

    def __init__(self, path, encoding='UTF8'):
        self.md = ''
        self.path = path
        self.encoding = encoding
        try:
            with open(path, 'r', encoding=encoding) as f:
                self.md = f.read()
                self.md.index(END_OF_CLASS)
                self.md.index(END_OF_LINK)
        except FileNotFoundError:
            self._print('Making a new mermaid markdown file to write. . .')
            with open(path, 'w', encoding=encoding) as f:
                f.write(INITIAL_TEMPLATE)
            self.md = INITIAL_TEMPLATE
        except ValueError:
            raise SyntaxError(f'The file "{path}" does not have the flounder indicator')


    @staticmethod
    def _print(msg):
        print(f'{TAG} {msg}')


    def _add_to(self, indicator, text):
        try:
            start_idx = self.md.index(indicator)
            self.md = self.md[:start_idx] + text + '\n' + self.md[start_idx:]
        except Exception:
            return


    @classmethod
    def _split_layers(cls, line: str):
        """
        Split the layers devided by '>' character
        :param line: Interpretable line
        :return: 2D Array consisted with each layer and individual class name
        """
        if len(line.split('>')) < 2:
            cls._syntax_error(line)
            return [], []
        layers = line.split('>')
        return list(map(lambda x: x.strip().split(' '), layers))
        # return [A.strip().split(' '), B.strip().split(' ')]


    def _link(self, line: str, link: str):
        """
        Interpret the line and make links
        :param line: Interpretable line
        :param link: Kind of link
        """
        result = ''
        A, B = self._split_layers(line)
        if not len(A) and not len(B):
            self._syntax_error(line)
            return False
        for a in A:
            for b in B:
                result += f'{a} {link} {b}\n'
        self._add_to(END_OF_LINK, result)





    def save(self):
        """
        Save field content to designated file (path)
        """
        try:
            with open(self.path, 'w', encoding=self.encoding) as f:
                f.write(self.md)
        except Exception:
            self._print("Error occurred at saving file")

    @classmethod
    def _syntax_error(cls, line):
        """
        Print error message
        :param line: Line content that caused this error
        """
        cls._print("Syntax Error : " + line)


    def edit(self):
        # TODO | > A 또는 | A > 등의 전체 지칭 만들기
        """
        class >>> [] NAME DESCRIPTION

        link >>> | D1 D2 D3 Dn > T1 T2 T3 Tn

        dot-link >>> & D1 D2 D3 Dn > T1 T2 T3 Tn

        delete link >>> ! D1 D2 D3 Dn > T1 T2 T3 Tn

        delete class >>> ! NAME
        """

        cmd = input(f'{TAG} >>> ')
        try:
            # LOOP
            while cmd != 'exit':
                if cmd[0:2] == '[]':
                    cmd = cmd[2:].strip()
                    cut = cmd.index(' ')
                    name = cmd[:cut]
                    description = cmd[cut+1:]
                    self._add_to(END_OF_CLASS, f'class {name} {{\n'
                                              f'{description}\n'
                                              f'}}')
                elif cmd[0] == '|':
                    cmd = cmd[1:].strip()
                    self._link(cmd, LINK)
                elif cmd[0] == '&':
                    cmd = cmd[1:].strip()
                    self._link(cmd, DOT_LINK)
                elif cmd[0] == '!':
                    cmd = cmd[1:].strip()
                    A, B = self._split_layers(cmd)
                    for a in A:
                        for b in B:
                            self.md = re.sub('\n* *(' + a + ') *[.-]{2}> *(' + b + ')', '', self.md)
                self.save()
                cmd = input(f'{TAG} >>> ')
        except KeyboardInterrupt:
            pass
