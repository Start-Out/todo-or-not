comment_symbols = {
    'python': {'line_comment': '#', 'block_comment': {'start': "'''", 'end': "'''"}},
    'java': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'javascript': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'c': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'c++': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'php': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'swift': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'ruby': {'line_comment': '#', 'block_comment': {'start': '=begin', 'end': '=end'}},
    'go': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'rust': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'kotlin': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'csharp': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'typescript': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'scala': {'line_comment': '//', 'block_comment': {'start': '/*', 'end': '*/'}},
    'shell': {'line_comment': '#', 'block_comment': {'start': ': \'', 'end': '\''}},
    'pascal': {'line_comment': '//', 'block_comment': {'start': '{', 'end': '}'}},
    'sql': {'line_comment': '--', 'block_comment': {'start': '/*', 'end': '*/'}}
}

file_extensions = {
    'python': ['.py'],
    'java': ['.java'],
    'javascript': ['.js'],
    'c': ['.c'],
    'c++': ['.cpp', '.hpp', '.cc', '.cxx'],
    'php': ['.php'],
    'swift': ['.swift'],
    'ruby': ['.rb'],
    'go': ['.go'],
    'rust': ['.rs'],
    'kotlin': ['.kt', '.kts'],
    'csharp': ['.cs'],
    'typescript': ['.ts'],
    'scala': ['.scala', '.sc'],
    'shell': ['.sh', '.bash'],
    'pascal': ['.pas', '.pp'],
    'sql': ['.sql']
}
