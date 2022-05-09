import re
from surongdan.extensions import db
from surongdan.models import module_def_table, module_custom_table

# 生成自定义模块的代码 
"""
- 传入参数:  mc_structure
            描述自定义模块结构的 object array
- 返回值  :  precode string
"""
g_gen_precode_i = 0
def gen_precode(mc_structure):
    # 依次遍历所有子 module
    param_base_index = 0
    gen_precode=''
    for module in mc_structure:
        global g_gen_precode_i
        
        if module['module_is_custom']:
            m = module_custom_table.query.get(int(module['module_id']))
            precode = m.module_custom_precode
            m_pnum = int(m.module_custom_param_num)
        else:
            m = module_def_table.query.get(int(module['module_id']))
            precode = m.module_def_precode
            m_pnum = int(m.module_def_param_num)
        
        g_gen_precode_i = 0
        def param_repl(matchobj):
            global g_gen_precode_i
            repl = '$' + str(param_base_index + g_gen_precode_i)
            g_gen_precode_i+=1
            return repl
        
        # 处理precode字段 : 将precode中的 $d 替换成 $(param_base_inde+i)
        precode = re.sub(r'\$\d+', param_repl, precode, m_pnum)
        param_base_index += m_pnum
        gen_precode += (precode +'\n\n')
    
    return gen_precode
