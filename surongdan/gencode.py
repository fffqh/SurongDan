import re
import pickle
from surongdan.extensions import db
from surongdan.models import module_def_table, project_table, layer_table


global_import_packge = ""


global_topo_nid_lst = []
global_node_lst = {}
# 检查网络结构
def check_structure(project_id):    
    p = project_table.query.get(project_id)
    project_layers = pickle.loads(p.project_layer)
    for layer_id in project_layers:
        global_node_lst[layer_id] = {'in':[], 'out':[]}
    project_edges = pickle.loads(p.project_edges)
    for edge in project_edges:
        global_node_lst[edge[0]]['out'].append(edge[1])
        global_node_lst[edge[1]]['in'].append(edge[0])
    open_node_lst = global_node_lst
    # 检查是否可以拓扑排序，即是否存在环
    while len(open_node_lst):
        find = False
        for nid, nvalue in open_node_lst.items():
            if len(nvalue['in']) == 0:
                find = True
                global_topo_nid_lst.append(nid)
                del open_node_lst[nid]
                break
        if not find:
            return False
    return True

# 生成模型代码
def gen_model_code(model_name):
    model_code = 'class ' + str(model_name) + '(nn.Module):\n'\
                    +'\tdef __init__(self):\n'\
                    +'\t\tsuper('+str(model_name)+', self).__init__()\n'
    for layer_id in global_topo_nid_lst:
        layer = layer_table.query.get(layer_id)
        module = module_def_table.query.get(int(layer.layer_module_id))        
        layer_param_list = pickle.loads(layer.layer_param_list)
        module_code = module.module_def_precode
        # 对代码模板进行参数替换
        for p in layer_param_list:
            module_code = re.sub(r'\$\d+', p, module_code, 1)
        # 生成一个block的代码
        model_code += '\t\tself.block' + layer_id + '=' + module_code + '\n'
    model_code += '\tdef forward(self, x):\n'
    for layer_id in global_topo_nid_lst:
        if len(global_node_lst[layer_id]['in']) == 0:
            model_code += ('\t\tx' + layer_id + '=self.block' + layer_id + '(x)\n')
            continue
        model_code += ('\t\taddfor_x'+layer_id+'='
        first_add = True
        for in_layer_id in global_node_lst[layer_id]['in']:
            if first_add:
                first_add = False
                model_code += ('x'+in_layer_id) 
            else:
                model_code += ('+x'+in_layer_id)
        model_code += '\n'
        model_code += '\t\tx'+layer_id+'self.block'+layer_id+'(addfor_x'+layer_id+')\n'
    model_code += '\t\treturn x'+global_topo_nid_lst[-1]
    return model_code

# 生成训练及测试代码
def gen_train_code(project_id):

    pass

# 主要函数：生成代码
def gen_code(project_id):
    # 1. import code 
    # 2. modol code
    # 3. train && test code
    pass
