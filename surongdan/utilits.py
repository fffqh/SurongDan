import os 

# 根据project_id在code目录下 检查是否有项目目录
def chk_proj_codedir(codepath, project_id):
    proj_dir = os.path.join(codepath, project_id)
    proj_dir_log = os.path.join(proj_dir, 'log')
    proj_dir_pic = os.path.join(proj_dir, 'pic')    
    if(not os.path.exists(proj_dir)):
        return False
    if(not os.path.exists(proj_dir_log)):
        return False
    if(not os.path.exists(proj_dir_pic)):
        return False

# 根据project_id在code目录下 创建项目目录 
def mk_proj_codedir(codepath, project_id):
    proj_dir = os.path.join(codepath, project_id)
    proj_dir_log = os.path.join(proj_dir, 'log')
    proj_dir_pic = os.path.join(proj_dir, 'pic')
    if(not os.path.exists(proj_dir)):
        os.mkdir(proj_dir)
        os.mkdir(proj_dir_log)
        os.mkdir(proj_dir_pic)
    else:
        if(not os.path.exists(proj_dir_log)):
            os.mkdir(proj_dir_log)
        if(not os.path.exists(proj_dir_pic)):
            os.mkdir(proj_dir_pic)
    return True

# 根据project_id在code目录下 删除项目目录 
def del_proj_codedir(codepath, project_id):
    proj_dir = os.path.join(codepath, project_id)
    if(os.path.exists(proj_dir)):
        os.removedirs(proj_dir)
    return True
