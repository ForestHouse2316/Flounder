import re

TAG = '[flounder]'
LINK = '-->'
DOT_LINK = '..>'
END_OF_CLASS = '%%END OF CLASS'
END_OF_LINK = '%%END OF LINK'
INITIAL_TEMPLATE = f'```mermaid\n\n{END_OF_CLASS}\n\n{END_OF_LINK}```'

class Flounder:

    def __init__(self, path):
        self.md = ''
        self.path = path
        try:
            with open(path, 'r') as f:
                self.md = f.read()
                if self.md.index(END_OF_CLASS) == -1 or self.md.index(END_OF_LINK) == -1:
                    raise SyntaxError(f'The file {path} does not have indicator of flounder')
        except FileNotFoundError:
            self._print('Making a new mermaid markdown file to write. . .')
            with open(path, 'w') as f:
                f.write(INITIAL_TEMPLATE)
            self.md = INITIAL_TEMPLATE


    @staticmethod
    def _print(msg):
        print(f'{TAG} {msg}')




    def add_to(self, indicator, text):
        try:
            start_idx = self.md.index(indicator)
            self.md = self.md[:start_idx] + text + '\n' + self.md[start_idx:]
        except Exception:
            return


    @classmethod
    def split_AB(cls, line: str):
        if len(line.split('>')) != 2:
            cls.syntax_error(line)
            return [], []
        A, B = line.split('>')
        return [A.strip().split(' '), B.strip().split(' ')]


    @classmethod
    def combine_AB(cls, line: str, link: str):
        result = ''
        A, B = cls.split_AB(line)
        if not len(A) and not len(B):
            cls.syntax_error(line)
            return False
        for a in A:
            for b in B:
                result += f'{a} {link} {b}\n'
        return result


    def save(self):
        try:
            with open(self.path, 'w') as f:
                f.write(self.md)
        except Exception:
            self._print("Error occurred at saving file")

    @classmethod
    def syntax_error(cls, line):
        cls._print("Syntax Error : " + line)


    def enter_editing_mode(self):
        # TODO | > A 또는 | A > 등의 전체 지칭 만들기
        """
        class >>> [] NAME DESCRIPTION

        link >>> | D1 D2 D3 Dn > T1 T2 T3 Tn

        dot-link >>> & D1 D2 D3 Dn > T1 T2 T3 Tn

        delete >>> ! D1 D2 D3 Dn > T1 T2 T3 Tn
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
                    self.add_to(END_OF_CLASS, f'class {name} {{\n'
                                              f'{description}\n'
                                              f'}}')
                elif cmd[0] == '|':
                    cmd = cmd[1:].strip()
                    self.add_to(END_OF_LINK, self.combine_AB(cmd, LINK))
                elif cmd[0] == '&':
                    cmd = cmd[1:].strip()
                    self.add_to(END_OF_LINK, self.combine_AB(cmd, DOT_LINK))
                elif cmd[0] == '!':
                    cmd = cmd[1:].strip()
                    A, B = self.split_AB(cmd)
                    for a in A:
                        for b in B:
                            self.md = re.sub('\n* *(' + a + ') *[.-]{2}> *(' + b + ')', '', self.md)
                self.save()
                cmd = input(f'{TAG} >>> ')
        except KeyboardInterrupt:
            pass
