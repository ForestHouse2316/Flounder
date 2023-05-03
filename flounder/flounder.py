import re

VER = '1.0.0b1'

TAG = '[flounder]'
LINK = '-->'
DOT_LINK = '..>'
END_OF_CLASS = '%%END OF CLASS'
END_OF_LINK = '%%END OF LINK'
INITIAL_TEMPLATE = f'```mermaid\nclassDiagram\n%%---\n\n\n{END_OF_CLASS}\n\n{END_OF_LINK}```'

class Flounder:

    def __init__(self, path, encoding='UTF8'):
        self.md = ''
        self.path = path
        self.encoding = encoding
        self.all_classes = []
        try:
            with open(path, 'r', encoding=encoding) as f:
                self.md = f.read()
                self.md.index(END_OF_CLASS)
                self.md.index(END_OF_LINK)
                self.all_classes = self._get_all_class()
        except FileNotFoundError:
            self._print('Making a new mermaid markdown file to write. . .')
            with open(path, 'w', encoding=encoding) as f:
                f.write(INITIAL_TEMPLATE)
            self.md = INITIAL_TEMPLATE
        except ValueError:
            raise SyntaxError(f'The file "{path}" does not have the flounder indicator')
        self._print("===========================")
        self._print(f"flounder version {VER}")
        self._print("Made by ForestHouse")
        self._print("===========================")


    @staticmethod
    def _print(msg):
        print(f'{TAG} {msg}')


    def _add_to(self, indicator, text):
        try:
            start_idx = self.md.index(indicator)
            self.md = self.md[:start_idx] + text + '\n' + self.md[start_idx:]
        except Exception:
            return

    def _get_all_class(self):
        """
        :return: Array of all class name
        """
        result = list(map(lambda x: x[6:-1].strip(), re.findall("class +.+ *?\{", self.md)))
        self._print("=====CLASS LIST=====")
        for r in result:
            self._print(r)
        return result


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


    def _link(self, line: str, link: str):
        """
        Interpret the line and make links
        :param line: Interpretable line
        :param link: Kind of link
        """
        result = ''
        layers = self._split_layers(line)
        for i in range(len(layers)):
            if layers[i] == ['']:
                layers[i] = self.all_classes
        for i in range(len(layers)-1):
            for a in layers[i]:
                for b in layers[i+1]:
                    result += f'{a} {link} {b}\n'
        self._add_to(END_OF_LINK, result)


    def _delete_class(self, name):
        """
        Delete class that has that name.
        :param name:
        :return:
        """
        self.md = re.sub('\n?class +' + name + ' *\{(.|\n)*?}', '', self.md)


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
        """
        class >>> [] NAME DESCRIPTION

        link >>> | D1 D2 D3 Dn > T1 T2 T3 Tn

        dot-link >>> & D1 D2 D3 Dn > T1 T2 T3 Tn

        delete link >>> ! D1 D2 D3 Dn > T1 T2 T3 Tn

        delete class >>> ! NAME
        """
        cmd = ''
        try:
            # LOOP
            while cmd != 'exit':
                cmd = input(f'{TAG} >>> ')
                if cmd[0:2] == '[]':
                    cmd = cmd[2:].strip()
                    cut = cmd.find(' ')
                    description = ''
                    if cut == -1:
                        name = cmd.strip()
                    else:
                        name = cmd[:cut].strip()
                        description = cmd[cut:].strip()
                    if description == '':
                        description = ' '
                    if name in self.all_classes:
                        self._delete_class(name)
                    else:
                        self.all_classes.append(name)
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
                    if cmd.find('>') == -1:
                        if cmd == '':
                            if input(f"{TAG} This command deletes all classes. Want to execute? [Y/N] : ").upper() == 'Y':
                                classes = self.all_classes
                            else:
                                continue
                        else:
                            classes = cmd.split(' ')
                        for name in classes:
                            self._delete_class(name)
                        for name in classes:
                            try:
                                self.all_classes.remove(name)
                            except ValueError:
                                pass
                    else:
                        layers = self._split_layers(cmd)
                        for i in range(len(layers)):
                            if layers[i] == ['']:
                                layers[i] = self.all_classes
                        for i in range(len(layers)-1):
                            for a in layers[i]:
                                for b in layers[i+1]:
                                    if a != '' and b != '':
                                        self.md = re.sub('\n? *' + a + ' *[.-]{2}> *' + b, '', self.md)
                self.save()
        except KeyboardInterrupt:
            pass
