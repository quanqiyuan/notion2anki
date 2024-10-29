import shutil
import genanki
import markdown
import re
import os
import pathlib
import urllib.parse
from pygments import highlight
from pygments.lexers import PythonLexer, JavaLexer, CppLexer, guess_lexer  # 根据需要添加更多语言
from pygments.formatters import HtmlFormatter


# 定义一个包含图片的Anki卡片模型
template_notion2anki = genanki.Model(
    1607392322,
    'Notion2Anki',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'Notion'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '<div class="left-align">{{Question}}</div>',
            'afmt': '''{{FrontSide}}<hr id="answer">
                <div class="left-align">{{Answer}}</div>
                <br>{{Notion}}
                <link rel="stylesheet" href="_tango.css">
            ''',
        },
    ],
    css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .left-align {
            text-align: left;
        }
        .wrapper {
            margin-left: 16px;
        }
        a {
            color: blue;
        }  # 使链接以蓝色显示
        img {
            max-width: 100%;  # 确保图片不会超过卡片宽度
            height: auto;  # 保持图片原始宽高比
        }
        pre {
            padding: 10px;
            border-radius: 5px;
            overflow: auto;
            font-family: 'Courier New', Courier, monospace; /* 等宽字体 */
        }
        code {
            color: #204a87;
            background: #f8f8f8;
            white-space: nowrap;
            font-family: 'Courier New', Courier, monospace; /* 等宽字体 */ 
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        td {
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            color: #444;
        }
        tr:nth-child(ddd) {
            background-color: #f9f9f9;
        }
    '''
)

# 语言到lexer的映射
lexer_mapping = {
    'python': PythonLexer(),
    'java': JavaLexer,
    'cpp': CppLexer,
    # 根据需要添加更多语言
}


def format_block_code(match_object):
    tab_string = match_object.group(1)
    code_language = match_object.group(2)
    code_content = match_object.group(3)
    #code_content = code_content.replace("\\", "\\\\")

    html_code = highlight(code_content, lexer_mapping.get(code_language, guess_lexer(code_content)), HtmlFormatter())
    tab_count = len(re.findall(' ', tab_string))
    html_code = f'<div>' + html_code + f'</div>'

    return html_code


def format_inline_code(match_object):
    result = match_object.group(1)
    result = result.replace(r'*', r'\*')
    #result = result.replace('\\', '\\\\')
    return rf'<code>{result}</code>'


# 列出Markdown文件，并为每个文件生成一张卡片
def notion2anki(notion_directory, media_directory):
    # 正则表达式，用于识别Markdown中的图片标签
    question_pattern = re.compile(r'^\s*#\s*(\S.*\S)+[\r\n]')
    date_pattern = re.compile(r'[^\r\n]*Date:\s*(\S.*\S)\s*[\r\n]')
    tag_pattern = re.compile(r'[^\r\n]*Tag:\s*(\S.*\S)\s*[\r\n]')
    action_pattern = re.compile(r'[^\r\n]*Action:\s*(\S.*\S)\s+\((\S.*\S)\)\s*[\r\n]')
    block_code_pattern = re.compile(r'( *)```(.*?)\n(.*?)```', re.DOTALL)
    inline_code_pattern = re.compile(r'`(.*?)`')
    block_equation_pattern = re.compile(r'([\r\n]\s*)\$(.*?)\$(\s*[\r\n])')
    inline_equation_pattern = re.compile(r'\$(.*?)\$')
    image_pattern = re.compile(r'!\[.*?]\((.*?)\)')

    cards = {}
    for filename in os.listdir(notion_directory):
        if filename.endswith(".md"):
            file_path = os.path.join(notion_directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

                question_match = question_pattern.match(content)
                question = question_match.group(1) if question_match else ''

                question = block_code_pattern.sub(lambda m:format_block_code(m), question)
                question = inline_code_pattern.sub(r'<code>\1</code>', question)
                question = block_equation_pattern.sub(r'\1\\\[\2\\\]\3', question)
                question = inline_equation_pattern.sub(r'\\\(\1\\\)', question)

                tag_match = tag_pattern.search(content)
                tag = tag_match.group(1) if tag_match else ''
                if not tag:
                    print(f'!!! {filename} is not tagged.')

                action_match = action_pattern.search(content)
                action_name, action_link = action_match.group(1, 2) if action_match else ('', '')
                notion = f'<a href="{action_link}">{action_name}</a>'

                content = tag_pattern.sub('', content)
                content = question_pattern.sub('', content)
                content = action_pattern.sub('', content)
                content = date_pattern.sub('', content)
                content = block_code_pattern.sub(lambda m:format_block_code(m), content)
                content = inline_code_pattern.sub(lambda m:format_inline_code(m), content)
                content = block_equation_pattern.sub(r'\1\\\[\2\\\]\3', content)
                content = inline_equation_pattern.sub(r'\\\(\1\\\)', content)

                # 查找并替换Markdown中的图片路径
                image_paths = re.findall(image_pattern, content)
                for image_path in image_paths:
                    image_abs_path = os.path.abspath(urllib.parse.unquote(os.path.join(notion_directory, image_path)))

                    new_image_path = urllib.parse.unquote(image_path)
                    while '%' in new_image_path:
                        new_image_path = urllib.parse.unquote(new_image_path)
                    new_image_path = f'{question}_{new_image_path}'
                    content = re.sub(image_path, new_image_path, content)

                    if pathlib.Path(image_abs_path).is_file():
                        image_file_name = os.path.join(media_directory, new_image_path)
                        shutil.copy(image_abs_path, image_file_name)
                    else:
                        print(f'File not found or invalid: {image_abs_path}')

                # 将Markdown内容转换为HTML
                double_underscore_replace = 'double-underscore'
                content = content.replace('__', double_underscore_replace)
                answer = markdown.markdown(content, output_format='html', extensions=['markdown.extensions.tables'])
                answer = answer.replace(double_underscore_replace, '__')

                if tag not in cards:
                    cards[tag] = set()
                cards[tag].add((question, answer, notion))
    return cards


deck_dict = {'default': 100000000, 'Python': 100000001, 'DFT': 100000002, 'SOC': 100000003, 'STA': 100000004, 'CPU': 100000005, '': 100000006}
