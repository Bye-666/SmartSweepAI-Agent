# 导入操作系统模块，用于路径操作
import os

def get_project_root() -> str:
    """
    获取工程根目录（无论脚本在哪个目录运行，都能返回正确的根目录）。
    原理：基于当前文件的绝对路径，向上推导到工程根目录。
    这个函数确保在任何地方调用时都能准确定位项目根目录，避免相对路径问题。
    
    Returns:
        str: 项目根目录的绝对路径
    """
    # 当前文件（path_utils.py）的绝对路径
    current_file = os.path.abspath(__file__)
    # 当前文件所在目录（utils/）
    current_dir = os.path.dirname(current_file)
    # 工程根目录（utils/ 的上一级目录）
    project_root = os.path.dirname(current_dir)
    return project_root

def get_abs_path(relative_path: str) -> str:
    """
    将工程内的相对路径转为绝对路径（统一路径基准）。
    该函数确保所有文件路径都相对于项目根目录，提高代码可移植性。
    
    Args:
        relative_path (str): 相对于工程根目录的路径，如 "config/rag.yml"
        
    Returns:
        str: 完整的绝对路径
    """
    # 获取项目根目录
    project_root = get_project_root()
    # 拼接根目录和相对路径，生成绝对路径
    return os.path.join(project_root, relative_path)
