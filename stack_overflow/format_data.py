import pandas as pd
from collections import Counter, defaultdict


def format_data(in_file, out_folder):
    orig = pd.read_csv(in_file)
    tool_map_large = {
        'Notepad++': 'Notepad++',
        'Visual Studio': 'Visual Studio',
        'Visual Studio Code': 'Visual Studio Code',
        'Xcode': 'Xcode',
        'Rider': 'Jetbrains',
        'Atom': 'Atom',
        'IntelliJ': 'Jetbrains',
        'PyCharm': 'Jetbrains',
        'Sublime Text': 'Sublime',
        'Webstorm': 'Jetbrains',
        'CLion': 'Jetbrains',
        'Eclipse': 'Eclipse',
        'Android Studio': 'Android Studio',
        'IPython/Jupyter': 'IPython',
        'Vim': '(Neo)vim',
        'Emacs': 'Emacs',
        'RAD Studio (Delphi, C++ Builder)': 'Other',
        'Neovim': '(Neo)vim',
        'Nano': 'Nano',
        'RStudio': 'RStudio',
        'PhpStorm': 'Jetbrains',
        'RubyMine': 'Jetbrains',
        'NetBeans': 'NetBeans',
        'GoLand': 'Jetbrains',
        'Spyder': 'Spyder',
        'Qt Creator': 'Qt Creator',
        'TextMate': 'NextMate',
    }
    tool_map_small = {
        'Notepad++': 'Notepad++',
        'Visual Studio': 'Visual Studio',
        'Visual Studio Code': 'Visual Studio Code',
        'Xcode': 'Other',
        'Rider': 'Jetbrains',
        'Atom': 'Atom',
        'IntelliJ': 'Jetbrains',
        'PyCharm': 'Jetbrains',
        'Sublime Text': 'Sublime',
        'Webstorm': 'Jetbrains',
        'CLion': 'Jetbrains',
        'Eclipse': 'Other',
        'Android Studio': 'Other',
        'IPython/Jupyter': 'Other',
        'Vim': '(Neo)vim',
        'Emacs': 'Other',
        'RAD Studio (Delphi, C++ Builder)': 'Other',
        'Neovim': '(Neo)vim',
        'Nano': 'Other',
        'RStudio': 'Other',
        'PhpStorm': 'Jetbrains',
        'RubyMine': 'Jetbrains',
        'NetBeans': 'Other',
        'GoLand': 'Jetbrains',
        'Spyder': 'Other',
        'Qt Creator': 'Other',
        'TextMate': 'Other',
    }
    dev_type_map = {
        'I used to be a developer by profession, but no longer am': 'pro',
        'I am a developer by profession': 'pro',
        'I code primarily as a hobby': 'novice',
        'None of these': 'novice',
        'I am not primarily a developer, but I write code sometimes as part of my work': 'novice',
        'I am learning to code': 'novice'
    }
    past_tool_names_pro = Counter()
    want_tool_names_pro = Counter()
    past_tool_names_all = Counter()
    want_tool_names_all = Counter()

    def update_counter(counter, response):
        tools = set([tool_map_large[tool] for tool in response.split(';')])

        for tool in tools:
            counter[tool] += 1 / len(tools)

    for dev_type, used, want in zip(orig['MainBranch'], orig['NEWCollabToolsHaveWorkedWith'], orig['NEWCollabToolsWantToWorkWith']):
        if pd.notna(used):
            if dev_type_map[dev_type] == 'pro':
                update_counter(past_tool_names_pro, used)
            update_counter(past_tool_names_all, used)

        if pd.notna(want):
            if dev_type_map[dev_type] == 'pro':
                update_counter(want_tool_names_pro, want)
            update_counter(want_tool_names_all, want)

    with open(f"{out_folder}/bar_data.csv", 'w+') as f:
        # write column headers
        tools = list(set(tool_map_large.values()))
        tools = sorted(tools, key=lambda x: -past_tool_names_pro[x])
        f.write(f"group,filter,{','.join(tools)}\n")
        for group, filter, counter in zip(['Used in the past (Professional)', 'Used in the past (All)', 'Want to use (Professional)', 'Want to use (All)'],
                                        ['pro', 'all', 'pro', 'all'],
                                        [past_tool_names_pro, past_tool_names_all, want_tool_names_pro, want_tool_names_all]):
            f.write(f'{group},{filter}')
            for k in tools:
                f.write(f',{counter[k]:.0f}')
            f.write('\n')

    transition_counts = Counter()
    have_used = Counter()
    tools_map_heatmap = tool_map_large
    def update_counter_2(to_tools, from_tools):
        if pd.notna(to_tools) and pd.notna(from_tools):
            to_tools = set([tools_map_heatmap[t] for t in to_tools.split(';')])
            from_tools = set([tools_map_heatmap[t] for t in from_tools.split(';')])
            for from_tool in from_tools:
                have_used[from_tool] += 1
                for to_tool in to_tools:
                    key = (from_tool, to_tool)
                    transition_counts[key] += 1

    for used, want in zip(orig['NEWCollabToolsHaveWorkedWith'], orig['NEWCollabToolsWantToWorkWith']):
        update_counter_2(used, want)

    with open(f"{out_folder}/heatmap.csv", 'w+') as f:
        # write column headers
        tools = list(set(tools_map_heatmap.values()))
        tools = sorted(tools, key=lambda x: -transition_counts[(x, x)]/have_used[x])
        f.write(f"Have used the tool in the past, want to use the tool, percentage\n")
        # for from_tool in tools:
        #     f.write(f'{from_tool}')
        #     sum_to = 0
        #     for to_tool in tools:
        #         sum_to += transition_counts[(from_tool, to_tool)]
        #     for to_tool in tools:
        #         f.write(f',{transition_counts[(from_tool, to_tool)]/sum_to:.4f}')
        #     f.write('\n')
        for from_tool in tools:
            for to_tool in tools:
                f.write(f'{from_tool},{to_tool},{100 * transition_counts[(from_tool, to_tool)]/have_used[from_tool]:.2f}\n')

if __name__ == "__main__":
    format_data('stack_overflow/orig_data.csv', 'stack_overflow')
