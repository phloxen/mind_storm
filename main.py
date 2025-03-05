import sys
import re
import textwrap
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QComboBox, QMessageBox, \
    QHBoxLayout, QGroupBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from graphviz import Digraph

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# 在设置环境变量时使用resource_path函数
current_dir = resource_path('.')
graphviz_bin_path = os.path.join(current_dir, 'graphviz')
os.environ["PATH"] += os.pathsep + graphviz_bin_path


class GraphvizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('基于Graphviz的思维导图设计器')
        self.setGeometry(100, 100, 1000, 800)

        # 设置窗口置顶
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # 现代配色方案
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                color: #2d3436;
            }
            QLabel {
                font-size: 24px;
                color: #636e72;
            }
            QPushButton {
                background-color: #0984e3;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 24px;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #74b9ff;
            }
            QTextEdit, QComboBox, QLineEdit {
                background-color: white;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                padding: 8px;
                font-size: 24px;
            }
            QGroupBox {
                border: 2px solid #dcdde1;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #0984e3;
                font-size: 24px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 标题部分
        header = QLabel('基于Graphviz的思维导图设计器')
        header.setFont(QFont('微软雅黑', 24, QFont.Bold))
        header.setStyleSheet("color: #0984e3;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # 输入部分
        input_group = QGroupBox("图表结构")
        input_layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "请输入层次结构（使用数字编号）：\n"
            "示例：\n"
            "1.主要主题\n"
            "1.1子主题1\n"
            "1.2子主题2\n"
            "1.2.1细节A\n"
            "2.另一个主题"
        )
        self.text_edit.setMinimumHeight(200)
        input_layout.addWidget(self.text_edit)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # 配置部分
        config_group = QGroupBox("图表设置")
        config_layout = QVBoxLayout()

        # 第一行设置
        row1 = QHBoxLayout()
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel("输出格式"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['PDF', 'PNG', 'SVG'])
        format_layout.addWidget(self.format_combo)
        row1.addLayout(format_layout)

        direction_layout = QVBoxLayout()
        direction_layout.addWidget(QLabel("布局方向"))
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(['从上到下 (TB)', '从左到右 (LR)'])
        direction_layout.addWidget(self.direction_combo)
        row1.addLayout(direction_layout)

        config_layout.addLayout(row1)

        # 第二行设置
        row2 = QHBoxLayout()
        style_layout = QVBoxLayout()
        style_layout.addWidget(QLabel("节点样式"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(['椭圆', '矩形', '圆形', '菱形', '普通文本'])
        style_layout.addWidget(self.shape_combo)
        row2.addLayout(style_layout)

        color_layout = QVBoxLayout()
        color_layout.addWidget(QLabel("节点颜色"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(['浅蓝 (#ecf0f1)', '樱花粉 (#fde3e7)', '薄荷绿 (#a3e4d7)', '薰衣草紫 (#d7bde2)',
                                   '蜜桃橙 (#f9e79f)', '珊瑚红 (#f5b7b1)'])
        row2.addLayout(color_layout)
        color_layout.addWidget(self.color_combo)

        config_layout.addLayout(row2)
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # 操作按钮
        self.generate_button = QPushButton('生成图表')
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #00b894;
                font-size: 24px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #55efc4;
            }
        """)
        self.generate_button.clicked.connect(self.generate_graph)
        main_layout.addWidget(self.generate_button, 0, Qt.AlignCenter)

        self.setLayout(main_layout)

    def generate_graph(self):
        try:
            dot = Digraph(comment='生成的图表', format=self.format_combo.currentText().lower())
            dot.attr(rankdir='TB' if '从上到下' in self.direction_combo.currentText() else 'LR',
                     fontname='Microsoft YaHei')

            text = self.text_edit.toPlainText().strip()
            lines = text.split('\n')

            parent_nodes = {}
            current_node = None

            max_width = 30  # 每个节点的最大字符宽度

            shape_mapping = {
                '矩形': 'box',
                '椭圆': 'ellipse',
                '圆形': 'circle',
                '菱形': 'diamond',
                '普通文本': 'plaintext'
            }

            for line in lines:
                match = re.match(r'(\d+(\.\d+)*)(.*)', line.strip())
                if match:
                    level_str, content = match.group(1), match.group(3).strip()
                    levels = list(map(int, level_str.split('.')))

                    # 如果内容以点开头则去除
                    if content.startswith('.'):
                        content = content[1:].strip()

                    # 使用 textwrap 填充文本以避免单词被截断
                    wrapped_content = '\\l'.join(textwrap.wrap(content, width=max_width))

                    if len(levels) == 1:
                        current_node = f"Node_{level_str}"
                        dot.node(current_node, label=wrapped_content,
                                 shape=shape_mapping[self.shape_combo.currentText()],
                                 style='filled',
                                 fillcolor=self.color_combo.currentText().split(' ')[-1][1:-1],
                                 fontcolor='black',
                                 fontsize='24',
                                 fontname='Microsoft YaHei')
                        parent_nodes[level_str] = current_node
                    else:
                        parent_level_str = '.'.join(map(str, levels[:-1]))
                        current_node = f"Node_{level_str}"
                        dot.node(current_node, label=wrapped_content,
                                 shape=shape_mapping[self.shape_combo.currentText()],
                                 style='filled',
                                 fillcolor=self.color_combo.currentText().split(' ')[-1][1:-1],
                                 fontcolor='black',
                                 fontsize='24',
                                 fontname='Microsoft YaHei')
                        parent_node = parent_nodes[parent_level_str]
                        dot.edge(parent_node, current_node, color='#636e72', style='solid')
                        parent_nodes[level_str] = current_node

                elif str(line) == '':
                    raise ValueError(f"请输入文本")

                else:
                    raise ValueError(f"无效的行格式: {line}")

            file_format = self.format_combo.currentText().lower()
            output_path_base = f'graph.{file_format}'
            output_path = output_path_base

            # Check if the file already exists and find a new name if necessary
            counter = 1
            while os.path.exists(output_path):
                output_path = f'graph_{counter}.{file_format}'
                counter += 1

            dot.render(filename=output_path.replace(f'.{file_format}', ''), cleanup=True, view=True)
            QMessageBox.information(self, "成功", f"图表已保存为 {output_path}")

        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphvizApp()
    ex.show()
    sys.exit(app.exec_())
