"""Prompts extracted verbatim from pinned upstream ASTs; MIT licenses adjacent."""

obtain_relevant_files_prompt = '\nPlease look through the following GitHub problem description and Repository structure and provide a list of files that one would need to edit to fix the problem.\n\n### GitHub Problem Description ###\n{problem_statement}\n\n###\n\n### Repository Structure ###\n{structure}\n\n###\n\nPlease only provide the full path and return at most 5 files.\nThe returned files should be separated by new lines ordered by most to least important and wrapped with ```\nFor example:\n```\nfile1.py\nfile2.py\n```\n'

obtain_relevant_functions_and_vars_from_compressed_files_prompt_more = "\nPlease look through the following GitHub Problem Description and the Skeleton of Relevant Files.\nIdentify all locations that need inspection or editing to fix the problem, including directly related areas as well as any potentially related global variables, functions, and classes.\nFor each location you provide, either give the name of the class, the name of a method in a class, the name of a function, or the name of a global variable.\n\n### GitHub Problem Description ###\n{problem_statement}\n\n### Skeleton of Relevant Files ###\n{file_contents}\n\n###\n\nPlease provide the complete set of locations as either a class name, a function name, or a variable name.\nNote that if you include a class, you do not need to list its specific methods.\nYou can include either the entire class or don't include the class name and instead include specific methods in the class.\n### Examples:\n```\nfull_path1/file1.py\nfunction: my_function_1\nclass: MyClass1\nfunction: MyClass2.my_method\n\nfull_path2/file2.py\nvariable: my_var\nfunction: MyClass3.my_method\n\nfull_path3/file3.py\nfunction: my_function_2\nfunction: my_function_3\nfunction: MyClass4.my_method_1\nclass: MyClass5\n```\n\nReturn just the locations wrapped with ```.\n"

def file_reasoning_prompt(file_content, bug_report):
    return f'A user is trying to fix a bug described in the following report:\n\n{bug_report}\n\nBelow is a code file from a repository:\n\n{file_content}\n\nExplain the purpose and functionality of this code in the context of the bug report. Focus on what this file does and whether it may be related to the bug.'

def file_ranking_prompt(file_reasoning, bug_report):
    return f'Below is a list of files from a repository and the reasonings behind the codes of these files:\n\n{file_reasoning}\n\nCan you rank the files based on the similarity of their reasoning to the bug report:\n\n{bug_report}\n\nPlease just return the list of ranked files.'

def element_reasoning_prompt(element_code, bug_report):
    return f'A user is trying to fix a bug described in the following report:\n\n{bug_report}\n\nBelow is a code element (a function, a class, or a global variable) in a file in a repository:\n\n{element_code}\n\nExplain the purpose and functionality of this code element in the context of the bug report. Focus on what this element does and whether it may be related to the bug.'

def element_ranking_prompt(file_elements_reasoning, bug_report):
    return f'You are provided with a list of code elements (functions, classes, and global variables) from a repository, along with an explanation of what each element does:\n\n{file_elements_reasoning}\n\nAlso you are given the following bug report:\n\n{bug_report}\n\nBased on the reasoning for each code element and the bug report, which of these elements are most likely related to the bug? Please just return a ranked list of the potentially buggy elements (keys in the file_elements_reasoning dictionary) without any further explanation.'

def show_project_structure(structure, spacing=0) -> str:
    """pprint the project structure"""
    pp_string = ''
    for key, value in structure.items():
        if '.' in key and '.py' not in key:
            continue
        if '.' in key:
            pp_string += ' ' * spacing + str(key) + '\n'
        else:
            pp_string += ' ' * spacing + str(key) + '/' + '\n'
        if 'classes' not in value:
            pp_string += show_project_structure(value, spacing + 4)
    return pp_string
