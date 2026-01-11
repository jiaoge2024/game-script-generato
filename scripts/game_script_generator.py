"""
游戏脚本生成器 (Game Script Generator)
一个强大的AI驱动的游戏设计文档生成工具

支持功能：
- 多种游戏类型脚本生成
- 模板化内容生成
- JSON结构化数据导出
- 批量生成支持
"""

import sys
import io
import json
import os
import argparse
import random
from datetime import datetime
from pathlib import Path

# 设置UTF-8编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# 配置区域
# ============================================================================

GAME_TYPES = {
    'rpg': {
        'name': '角色扮演游戏',
        'default_theme': 'fantasy',
        'description': '以角色成长和剧情体验为核心的游戏类型',
        'keywords': ['rpg', 'role-playing', '角色扮演', '角色游戏']
    },
    'adventure': {
        'name': '冒险游戏',
        'default_theme': 'exploration',
        'description': '以探索和解谜为核心的叙事游戏',
        'keywords': ['adventure', 'avg', '冒险', '探险']
    },
    'visual_novel': {
        'name': '视觉小说',
        'default_theme': 'romance',
        'description': '以剧情和角色互动为主的文字冒险游戏',
        'keywords': ['visual_novel', 'vn', 'galgame', '视觉小说', '恋爱模拟']
    },
    'horror': {
        'name': '恐怖游戏',
        'default_theme': 'supernatural',
        'description': '营造恐怖氛围的生存游戏',
        'keywords': ['horror', '恐怖', '惊悚', 'survival_horror']
    },
    'action': {
        'name': '动作游戏',
        'default_theme': 'combat',
        'description': '以操作技巧和战斗为核心的快节奏游戏',
        'keywords': ['action', '动作', 'act', '格斗', '射击']
    },
    'strategy': {
        'name': '策略游戏',
        'default_theme': 'warfare',
        'description': '需要战略思考和资源管理的游戏',
        'keywords': ['strategy', 'slg', '策略', '战略', '战棋']
    },
    'simulation': {
        'name': '模拟经营',
        'default_theme': 'management',
        'description': '模拟现实经营活动的游戏',
        'keywords': ['simulation', 'sim', '模拟', '经营', '养成']
    },
    'puzzle': {
        'name': '解谜游戏',
        'default_theme': 'mystery',
        'description': '以解谜和逻辑推理为核心的游戏',
        'keywords': ['puzzle', '解谜', '密室', '推理']
    }
}

THEME_MAP = {
    'fantasy': {'name': '奇幻', 'style': '史诗、魔法、冒险'},
    'scifi': {'name': '科幻', 'style': '未来、科技、太空'},
    'modern': {'name': '现代', 'style': '都市、现实、生活'},
    'cyberpunk': {'name': '赛博朋克', 'style': '高科技、低生活、反乌托邦'},
    'post_apocalyptic': {'name': '末世', 'style': '废土、生存、重建'},
    'supernatural': {'name': '超自然', 'style': '灵异、恐怖、神秘'},
    'historical': {'name': '历史', 'style': '古代、战争、文化'},
    'steampunk': {'name': '蒸汽朋克', 'style': '蒸汽、机械、维多利亚'},
    'wuxia': {'name': '武侠', 'style': '江湖、武术、侠义'},
    'xianxia': {'name': '仙侠', 'style': '修真、仙界、长生'}
}

LENGTH_CONFIG = {
    'short': {'word_count': 5000, 'chapters': 2, 'npcs': 3},
    'medium': {'word_count': 10000, 'chapters': 4, 'npcs': 5},
    'long': {'word_count': 20000, 'chapters': 7, 'npcs': 8}
}

# ============================================================================
# 模板数据
# ============================================================================

CHARACTER_NAMES = {
    'fantasy': {
        'male': ['亚瑟', '凯尔', '雷恩', '艾伦', '德里克', '索恩', '加雷斯', '卢卡斯'],
        'female': ['艾莉亚', '塞拉菲娜', '伊莎贝拉', '莉莉安', '罗莎琳', '艾薇', '娜塔莉', '索菲亚']
    },
    'scifi': {
        'male': ['凯尔', '雷克斯', '诺瓦', '泽塔', '阿尔法', '欧米伽', '赛特', '泰坦'],
        'female': ['莱拉', '尼克斯', '奥拉', '维加', '艾拉', '露娜', '塞拉', '星尘']
    },
    'modern': {
        'male': ['杰克', '瑞恩', '亚历克斯', '迈克', '大卫', '克里斯', '汤姆', '丹'],
        'female': ['艾玛', '莎拉', '艾米丽', '杰西卡', '丽莎', '安娜', '凯特', '米娅']
    }
}

PLOT_TEMPLATES = {
    'rpg': [
        "英雄之旅：平凡少年被卷入预言，踏上拯救世界的冒险",
        "复仇之路：主角家园被毁，踏上寻找真相和复仇的旅程",
        "王权争夺：各方势力争夺王位，主角选择阵营并改变命运",
        "神明觉醒：远古神明苏醒，主角成为唯一能对抗它的存在",
        "时空穿梭：世界面临崩坏，主角穿越不同时间线修复历史"
    ],
    'adventure': [
        "神秘寻宝：根据古老地图寻找失落文明的宝藏",
        "孤岛求生：飞机失事后在神秘岛屿求生并揭示岛屿秘密",
        "侦探破案：调查一系列看似无关的案件背后的真相",
        "考古探险：探索古代遗迹，解开文明消失之谜",
        "深海探索：潜入深海，发现隐藏在海底的古代文明"
    ],
    'horror': [
        "幽灵庄园：被困在充满怨灵的古老庄园中寻找出路",
        "病毒爆发：在丧尸横行的城市中寻找解药和幸存者",
        "心理恐怖：在封闭环境中逐渐分不清现实与幻觉",
        "邪教仪式：深入邪教巢穴，阻止召唤邪神的仪式",
        "诅咒村落：进入被诅咒的村落，揭开村民失踪真相"
    ]
}

# ============================================================================
# 生成器类
# ============================================================================

class GameScriptGenerator:
    """游戏脚本生成器主类"""

    def __init__(self, game_type='rpg', theme='fantasy', length='medium',
                 platform='PC', style='epic', output_dir='output'):
        """
        初始化生成器

        Args:
            game_type: 游戏类型
            theme: 游戏主题
            length: 脚本长度 (short/medium/long)
            platform: 目标平台
            style: 游戏风格
            output_dir: 输出目录
        """
        self.game_type = self._normalize_game_type(game_type)
        self.theme = self._normalize_theme(theme)
        self.length = length
        self.platform = platform
        self.style = style
        self.output_dir = Path(output_dir)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 根据长度配置生成规模
        config = LENGTH_CONFIG.get(length, LENGTH_CONFIG['medium'])
        self.word_count = config['word_count']
        self.chapter_count = config['chapters']
        self.npc_count = config['npcs']

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _normalize_game_type(self, game_type):
        """规范化游戏类型"""
        game_type = game_type.lower().strip()
        # 直接匹配
        if game_type in GAME_TYPES:
            return game_type
        # 关键词匹配
        for gt, info in GAME_TYPES.items():
            if any(kw in game_type for kw in info['keywords']):
                return gt
        # 默认返回rpg
        return 'rpg'

    def _normalize_theme(self, theme):
        """规范化主题"""
        theme = theme.lower().strip()
        # 直接匹配
        if theme in THEME_MAP:
            return theme
        # 关键词匹配
        for t in THEME_MAP:
            if t in theme:
                return t
        # 根据游戏类型返回默认主题
        return GAME_TYPES[self.game_type]['default_theme']

    def generate_game_name(self):
        """生成游戏名称"""
        prefixes = ['永恒', '命运', '星辰', '暗影', '传说', '幻境', '龙魂', '时光']
        suffixes = ['之旅', '契约', '纪元', '传说', '之歌', '之影', '觉醒', '战争']

        theme_prefixes = {
            'scifi': ['星际', '银河', '量子', '虚空', '赛博', '机甲'],
            'fantasy': ['龙之', '魔法', '精灵', '元素', '神域', '英雄'],
            'horror': ['噩梦', '怨灵', '黑暗', '深渊', '诅咒', '寂静'],
            'modern': ['都市', '罪恶', '迷途', '真相', '暗流', '破晓']
        }

        theme_suffixes = {
            'scifi': ['战线', '漫游', '计划', '前线', '危机', '崛起'],
            'fantasy': ['誓约', '远征', '传说', '史诗', '王者', '荣耀'],
            'horror': ['之夜', '逃脱', '游戏', '侵袭', '梦魇', '恐惧'],
            'modern': ['行动', '档案', '追逐', '阴谋', '破局', '救赎']
        }

        prefixes = theme_prefixes.get(self.theme, prefixes)
        suffixes = theme_suffixes.get(self.theme, suffixes)

        name = f"{random.choice(prefixes)}{random.choice(suffixes)}"
        return name

    def generate_worldview(self):
        """生成世界观设定"""
        theme_name = THEME_MAP[self.theme]['name']
        theme_style = THEME_MAP[self.theme]['style']

        worldview = f"""
## 2. 世界观设定

### 2.1 世界背景

**时代设定：** {theme_name}世界

这是一个{theme_style}的世界。"""

        # 根据主题添加特定描述
        if self.theme == 'fantasy':
            worldview += f"""
大陆被划分为三个主要区域：北方的冰封荒原、中央的魔法王国和南方的沙漠帝国。
魔法在这个世界中是真实存在的力量，少数人天生具有操控元素的能力。
千年前的"魔法大战"几乎摧毁了整个文明，如今世界仍在恢复之中。"""
        elif self.theme == 'scifi':
            worldview += f"""
人类已经跨入星际时代，建立了横跨多个星系的联合政府。
科技高度发达，人工智能和基因改造已成为日常生活的一部分。
但在繁荣的表象下，古老的威胁正在宇宙深处苏醒。"""
        elif self.theme == 'horror':
            worldview += f"""
这个世界表面看起来正常，但暗地里充满了无法解释的超自然现象。
有些人声称看到了来自另一个世界的存在，但大多数人选择不相信。
直到那一天到来，所有人的认知都被彻底颠覆。"""

        worldview += f"""

### 2.2 世界规则

**核心规则：**
- 力量体系有待玩家探索和发现
- 世界中存在多个势力，彼此之间关系复杂
- 重要决定会影响世界走向"""

        return worldview

    def generate_characters(self):
        """生成角色设定"""
        theme_names = CHARACTER_NAMES.get(self.theme, CHARACTER_NAMES['modern'])
        plot = random.choice(PLOT_TEMPLATES.get(self.game_type, PLOT_TEMPLATES['rpg']))

        characters = f"""
## 3. 角色设计

### 3.1 主角

**姓名：** {random.choice(theme_names['male'])}

**背景：**
{plot.split('：')[1] if '：' in plot else plot}

**性格特点：**
- 坚定不移的意志
- 对未知充满好奇
- 愿意为他人牺牲

**初始能力：**
- 基础战斗技能
- 特殊天赋（随游戏进程觉醒）

### 3.2 主要NPC"""

        # 生成主要NPC
        npcs = [
            {'role': '盟友', 'name': random.choice(theme_names['female']), 'trait': '智慧与支持'},
            {'role': '导师', 'name': random.choice(theme_names['male']), 'trait': '神秘与指引'},
            {'role': '对手', 'name': random.choice(theme_names['male']), 'trait': '强大与复杂'},
            {'role': '中立', 'name': random.choice(theme_names['female']), 'trait': '信息与交易'},
        ]

        for i, npc in enumerate(npcs[:self.npc_count]):
            characters += f"""

**NPC-{i+1}：{npc['name']}**
- **身份：** {npc['role']}
- **特点：** {npc['trait']}
- **背景：** 与主角的命运紧密相连"""

        characters += """

### 3.3 角色关系图

```
    主角
      ├── 盟友（支持者）
      ├── 导师（指引者）
      ├── 对手（竞争者）
      └── 中立（情报商）
```"""

        return characters

    def generate_plot(self):
        """生成剧情大纲"""
        plot = f"""
## 4. 剧情大纲

### 4.1 序章：命运的开始

主角的日常生活被意外打破，一个神秘事件将他/她推向了未知的冒险之路。
在导师的指引下，主角踏上了改变命运的旅程。

### 4.2 主线剧情

"""

        # 生成章节
        chapter_names = [
            "初入未知", "力量觉醒", "真相浮现", "背水一战",
            "绝境求生", "最终决战", "新的开始"
        ]

        for i in range(min(self.chapter_count, len(chapter_names))):
            chapter_num = i + 1
            chapter_name = chapter_names[i]

            plot += f"""
#### 第四章{chapter_num}：{chapter_name}

**剧情概述：**
主角在旅程中面临新的挑战和考验。{chapter_name}标志着故事的重要转折点。

**关键事件：**
- 发现关键线索
- 遭遇重要敌人
- 做出重要选择
- 获得力量提升

**章节BOSS：**
{self._generate_boss_description(chapter_num)}
"""

        # 添加支线任务
        plot += f"""
### 4.3 支线任务

1. **失踪的物品** - 帮助村民找回丢失的重要物品
2. **隐藏的宝藏** - 根据线索寻找传说中的宝藏
3. **旧日的恩怨** - 解决两个家族之间的长期纷争
4. **神秘的请求** - 接受陌生人的委托，发现背后的真相

### 4.4 结局分支

**真结局：**
收集所有线索，做出正确选择，揭开世界真相，迎来真正的新开始。

**普通结局：**
完成主线任务，但错过了某些关键信息，世界得到拯救但留下遗憾。

**坏结局：**
在关键节点做出错误选择，导致不可挽回的后果。"""

        return plot

    def _generate_boss_description(self, chapter_num):
        """生成BOSS描述"""
        boss_types = [
            "堕落的守护者", "远古魔兽", "黑暗骑士", "邪恶法师",
            "机械巨兽", "幽灵领主", "变异生物", "背叛的盟友"
        ]
        boss_type = boss_types[(chapter_num - 1) % len(boss_types)]

        return f"""
**名称：** {boss_type}
**特点：** 拥有强大的力量和独特的战斗机制
**弱点：** 需要玩家观察发现
**掉落：** 关键道具/装备"""

    def generate_dialogue_sample(self):
        """生成对话脚本示例"""
        return """
## 5. 对话脚本示例

### 5.1 开场场景

**[场景：夕阳下的村庄广场]**

**导师：**
"你终于来了。我等你很久了。"

**主角：**
"你是谁？为什么找我？"

**导师：**
"这些问题以后会有答案。现在，你只需要知道一件事——世界需要你。"

**主角：**
"我？一个普通人？这太荒谬了。"

**导师：**
"血统会说话，命运会召唤。跟我来吧，时间不多了。"

### 5.2 选择分支设计

**[关键选择点]**

导师伸出手，等待着你的决定。

**[选项A：接受邀请]**
> 主角踏上冒险之路，主线剧情继续推进

**[选项B：拒绝邀请]**
> 导师留下神秘道具后离开，主角遭遇危机后被迫踏上旅程

**[选项C：询问更多细节]**
> 导师透露部分信息，但表示真相需要自己探索"""

    def generate_level_design(self):
        """生成关卡设计"""
        levels = f"""
## 6. 关卡/场景设计

### 关卡1：新手教程区域

**场景描述：**
一个相对安全的起始区域，玩家在此学习基础操作。

**主要内容：**
- 基础战斗教学
- 移动和交互教学
- 引导NPC对话
- 简单的收集任务

**奖励：**
- 初始装备
- 基础道具
- 游戏货币

### 关卡2：第一个危险区域

**场景描述：**
危险的野外区域，玩家首次遭遇真正的敌人。

**主要内容：**
- 中等难度战斗
- 简单解谜元素
- 第一个BOSS战
- 重要剧情推进

**奖励：**
- 关键剧情道具
- 新技能解锁
- 装备升级"""

        # 根据长度添加更多关卡
        if self.length in ['medium', 'long']:
            levels += """

### 关卡3：隐藏遗迹

**场景描述：**
古代文明留下的神秘遗迹，充满机关和秘密。

**主要内容：**
- 复杂解谜
- 多条路径选择
- 隐藏宝箱
- 中期BOSS战

**奖励：**
- 强力装备
- 稀有道具
- 世界观碎片"""

        return levels

    def generate_system_design(self):
        """生成系统设计"""
        return """
## 7. 系统设计

### 7.1 战斗系统

**核心机制：**
- 回合制/即时战斗（根据游戏类型）
- 技能连携系统
- 元素相克机制
- 队伍协作

**成长要素：**
- 经验值升级
- 技能点分配
- 装备强化
- 天赋树

### 7.2 经济系统

**货币类型：**
- 金币：基础货币
- 宝石：高级货币
- 声望：特殊货币

**获取方式：**
- 任务奖励
- 战利品
- 交易出售
- 探索发现

### 7.3 任务系统

**任务类型：**
- 主线任务：推动剧情发展
- 支线任务：丰富世界观
- 日常任务：重复可做
- 隐藏任务：特殊触发

### 7.4 成就系统

**成就类别：**
- 剧情成就
- 战斗成就
- 探索成就
- 收藏成就"""

    def generate_appendix(self):
        """生成附录"""
        game_name = self.generate_game_name()
        return f"""
## 8. 附录

### 8.1 术语表

- **核心力量：** 世界中的特殊能量形式
- **远古文明：** 现世界之前存在的高等文明
- **预言者：** 能够预见未来的神秘群体

### 8.2 参考作品

本游戏设计参考了以下作品的元素：
- 经典RPG游戏的核心机制
- 现代叙事游戏的剧情设计
- 日式和西式RPG的融合风格

### 8.3 后续扩展方向

**DLC计划：**
- 新角色剧情线
- 额外章节内容
- 挑战模式
- 多人合作模式

**续作可能性：**
- 本作结局留有续作伏笔
- 可开发前传或外传作品

---

**文档信息**
- 游戏名称：{game_name}
- 文档版本：1.0
- 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 预计字数：约{self.word_count}字
- 设计者：AI游戏脚本生成器

*本文档由游戏脚本生成器自动生成，仅供参考*
"""

    def generate_full_script(self):
        """生成完整脚本"""
        game_name = self.generate_game_name()

        script = f"""# {game_name} - 游戏设计文档

## 1. 游戏概述

**游戏名称：** {game_name}

**游戏类型：** {GAME_TYPES[self.game_type]['name']}

**核心玩法概述：**
{random.choice(PLOT_TEMPLATES.get(self.game_type, PLOT_TEMPLATES['rpg']))}

**目标玩家群体：**
- 年龄：16-35岁
- 偏好：剧情向游戏
- 平台：{self.platform}

**年龄分级：**
- T级（青少年）- 适合16岁以上玩家
- 内容包含：幻想暴力、轻度语言
"""

        # 添加各个模块
        script += self.generate_worldview()
        script += self.generate_characters()
        script += self.generate_plot()
        script += self.generate_dialogue_sample()
        script += self.generate_level_design()
        script += self.generate_system_design()
        script += self.generate_appendix()

        return script

    def save_script(self, script, export_json=False):
        """保存脚本到文件"""
        game_type_name = GAME_TYPES[self.game_type]['name']
        theme_name = THEME_MAP[self.theme]['name']

        # 生成文件名
        filename = f"{self.game_type}_{self.theme}_{self.timestamp}.md"
        filepath = self.output_dir / filename

        # 写入Markdown文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(script)

        print(f"✓ 脚本已生成: {filepath}")

        # 可选：导出JSON
        if export_json:
            json_data = self._export_json(script)
            json_filename = f"{self.game_type}_{self.theme}_{self.timestamp}.json"
            json_filepath = self.output_dir / json_filename

            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            print(f"✓ JSON数据已导出: {json_filepath}")

        return str(filepath)

    def _export_json(self, script):
        """导出JSON结构化数据"""
        return {
            'metadata': {
                'game_type': self.game_type,
                'game_type_name': GAME_TYPES[self.game_type]['name'],
                'theme': self.theme,
                'theme_name': THEME_MAP[self.theme]['name'],
                'length': self.length,
                'word_count': self.word_count,
                'platform': self.platform,
                'style': self.style,
                'generated_at': self.timestamp,
                'chapters': self.chapter_count,
                'npcs': self.npc_count
            },
            'content': {
                'markdown': script,
                'title': self.generate_game_name()
            }
        }


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='游戏脚本生成器 - 生成完整的游戏设计文档'
    )

    parser.add_argument(
        '--type', '-t',
        default='rpg',
        choices=list(GAME_TYPES.keys()),
        help='游戏类型 (默认: rpg)'
    )

    parser.add_argument(
        '--theme',
        default='fantasy',
        choices=list(THEME_MAP.keys()),
        help='游戏主题 (默认: fantasy)'
    )

    parser.add_argument(
        '--length', '-l',
        default='medium',
        choices=['short', 'medium', 'long'],
        help='脚本长度 (默认: medium)'
    )

    parser.add_argument(
        '--platform', '-p',
        default='PC',
        help='目标平台 (默认: PC)'
    )

    parser.add_argument(
        '--style', '-s',
        default='epic',
        help='游戏风格 (默认: epic)'
    )

    parser.add_argument(
        '--output', '-o',
        default='output',
        help='输出目录 (默认: output)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='同时导出JSON格式'
    )

    parser.add_argument(
        '--batch', '-b',
        help='批量生成配置文件路径'
    )

    args = parser.parse_args()

    # 批量生成模式
    if args.batch:
        with open(args.batch, 'r', encoding='utf-8') as f:
            batch_config = json.load(f)

        for item in batch_config.get('games', []):
            generator = GameScriptGenerator(
                game_type=item.get('type', 'rpg'),
                theme=item.get('theme', 'fantasy'),
                length=item.get('length', 'medium'),
                platform=item.get('platform', 'PC'),
                style=item.get('style', 'epic'),
                output_dir=item.get('output', 'output')
            )

            script = generator.generate_full_script()
            generator.save_script(script, export_json=args.json)
        return

    # 单次生成模式
    print(f"正在生成{GAME_TYPES[args.type]['name']}脚本...")

    generator = GameScriptGenerator(
        game_type=args.type,
        theme=args.theme,
        length=args.length,
        platform=args.platform,
        style=args.style,
        output_dir=args.output
    )

    script = generator.generate_full_script()
    filepath = generator.save_script(script, export_json=args.json)

    print(f"\n✓ 生成完成！")
    print(f"  游戏类型: {GAME_TYPES[args.type]['name']}")
    print(f"  主题: {THEME_MAP[args.theme]['name']}")
    print(f"  预计字数: 约{LENGTH_CONFIG[args.length]['word_count']}字")
    print(f"  文件路径: {filepath}")


if __name__ == "__main__":
    main()
