from pickletools import optimize
import re
import copy
import pickle
from surongdan.extensions import db
from surongdan.models import module_def_table, project_table,project_superparam_table,dataset_table,layer_table


global_model_class = "class myReshapeLinear(nn.Linear):\n\
\tdef __init__(self, in_features: int, out_features: int, bias: bool = True, device=None, dtype=None) -> None:\n\
\t\tsuper(myReshapeLinear, self).__init__(in_features, out_features, bias)\n\
\tdef forward(self, x: Tensor) -> Tensor:\n\
\t\tx = x.reshape(x.shape[0], -1)\n\
\t\treturn F.linear(x, self.weight, self.bias)\n\
"


global_import_packge = "import time\n\
import numpy as np\n\
from torchvision import transforms\n\
from torchvision.datasets import {0}\n\
from torch.utils.data import DataLoader\n\
import matplotlib.pyplot as plt\n\
import torch.nn as nn\n\
import torch.optim as optim\n\
from torch import Tensor\n\
import torch.nn.functional as F\n"

global_batch_size = \
"train_batch_size = {0}\n\
test_batch_size = {1}\n"

global_deal_data = "transform = transforms.Compose([transforms.ToTensor(),transforms.Normalize([0.5],[0.5])])\n\
data_train = {0}('~/data/', train=True, transform=transform,target_transform=None, download=True)\n\
data_test  = {1}('~/data/', train=False, transform=transform,target_transform=None, download=True)\n\
train_loader = DataLoader(data_train, batch_size=train_batch_size, shuffle=True)\n\
test_loader = DataLoader(data_test,batch_size=test_batch_size,shuffle=True)\n\
"
global_train_test_code = "model = myModel()\n\
print(model)\n\
num_epochs = {0}\n\
criterion = nn.{1}\n\
LR = {2}\n\
optimizer = optim.{3}(model.parameters(), LR)\n\
train_losses = []\n\
train_acces = []\n\
eval_losses = []\n\
eval_acces = []\n\
print(\"start training...\")\n\
start_time = time.time()\n\
for epoch in range(num_epochs):\n\
\ttrain_loss = 0\n\
\ttrain_acc = 0\n\
\tmodel.train()\n\
\tfor img, label in train_loader:\n\
\t\tout = model(img)\n\
\t\tloss = criterion(out, label)\n\
\t\toptimizer.zero_grad()\n\
\t\tloss.backward()\n\
\t\toptimizer.step()\n\
\t\ttrain_loss += loss\n\
\t\t_, pred = out.max(1)\n\
\t\tnum_correct = (pred == label).sum().item()\n\
\t\tacc = num_correct / img.shape[0]\n\
\t\ttrain_acc += acc\n\
\ttrain_losses.append(train_loss / len(train_loader))\n\
\ttrain_acces.append(train_acc / len(train_loader))\n\
\teval_loss = 0\n\
\teval_acc = 0\n\
\tmodel.eval()\n\
\tfor img, label in test_loader:\n\
\t\tout = model(img)\n\
\t\tloss = criterion(out, label)\n\
\t\toptimizer.zero_grad()\n\
\t\tloss.backward()\n\
\t\toptimizer.step()\n\
\t\teval_loss += loss\n\
\t\t_, pred = out.max(1)\n\
\t\tnum_correct = (pred == label).sum().item()\n\
\t\tacc = num_correct / img.shape[0]\n\
\t\teval_acc += acc\n\
\teval_losses.append(eval_loss / len(test_loader))\n\
\teval_acces.append(eval_acc / len(test_loader))\n\
"
global_train_test_code_print = \
"\tprint('epoch:{},Train Loss:{:.4f},Train Acc:{:.4f},Test Loss:{:.4f},Test Acc:{:.4f}'.format(epoch, train_loss / len(train_loader),train_acc / len(train_loader),eval_loss / len(test_loader),eval_acc / len(test_loader)))\n\
\tstop_time = time.time()\n\
\tprint('time is:{:.4f}s'.format(stop_time-start_time))\n\
print('end training.')\n"


global_train_test_code_bak = "model = myModel()\n\
print(model)\n\
num_epochs = {0}\n\
criterion = nn.{1}\n\
LR = {2}\n\
optimizer = optim.{3}(model.parameters(), LR)\n\
train_losses = []\n\
train_acces = []\n\
eval_losses = []\n\
eval_acces = []\n\
print(\"start training...\")\n\
start_time = time.time()\n\
for epoch in range(num_epochs):\n\
\ttrain_loss = 0\n\
\ttrain_acc = 0\n\
\tmodel.train()\n\
\tfor img, label in train_loader:\n\
\t\tout = model(img)\n\
\t\tloss = criterion(out, label)\n\
\t\toptimizer.zero_grad()\n\
\t\tloss.backward()\n\
\t\toptimizer.step()\n\
\t\ttrain_loss += loss\n\
\t\t_, pred = out.max(1)\n\
\t\tnum_correct = (pred == label).sum().item()\n\
\t\tacc = num_correct / img.shape[0]\n\
\t\ttrain_acc += acc\n\
\ttrain_losses.append(train_loss / len(train_loader))\n\
\ttrain_acces.append(train_acc / len(train_loader))\n\
\teval_loss = 0\n\
\teval_acc = 0\n\
\tmodel.eval()\n\
\tfor img, label in test_loader:\n\
\t\tout = model(img)\n\
\t\tloss = criterion(out, label)\n\
\t\toptimizer.zero_grad()\n\
\t\tloss.backward()\n\
\t\toptimizer.step()\n\
\t\teval_loss += loss\n\
\t\t_, pred = out.max(1)\n\
\t\tnum_correct = (pred == label).sum().item()\n\
\t\tacc = num_correct / img.shape[0]\n\
\t\teval_acc += acc\n\
\teval_losses.append(eval_loss / len(test_loader))\n\
\teval_acces.append(eval_acc / len(test_loader))\n\
\tprint(\'epoch:\{\},Train Loss:\{:.4f\},Train Acc:\{:.4f\},\',\'Test Loss:\{:.4f\},Test Acc:\{:.4f\}\'.format(epoch, train_loss / len(train_loader),train_acc / len(train_loader),eval_loss / len(test_loader),eval_acc / len(test_loader)))\n\
\tstop_time = time.time()\n\
\tprint(\"time is:{:.4f}s\".format(stop_time-start_time))\n\
print(\"end training.\")\n\
"

global_loss_visualize = "plt.figure()\n\
plt.title(\"loss\")\n\
line1,=plt.plot(np.arange(len(train_losses)), train_losses)\n\
line2,=plt.plot(np.arange(len(eval_losses)), eval_losses)\n\
plt.legend(handles=[line1,line2], labels=['train loss','eval loss'])\n\
plt.savefig(\"{0}\")\n\
"

global_acc_visualize = "plt.figure()\n\
plt.title(\"acc\")\n\
line1,=plt.plot(np.arange(len(train_acces)), train_acces)\n\
line2,=plt.plot(np.arange(len(eval_acces)), eval_acces)\n\
plt.legend(handles=[line1,line2], labels=['train acc','eval acc'])\n\
plt.savefig(\"{0}\")\n\
"

global_topo_nid_lst = []
global_node_lst = {}
# 检查网络结构
def check_structure(project_id):    
    p = project_table.query.get(project_id)
    project_layers = pickle.loads(p.project_layer)
    for layer_id in project_layers:
        global_node_lst[layer_id] = {'in':[], 'out':[]}
    project_edges = pickle.loads(p.project_edge)
    for edge in project_edges:
        global_node_lst[edge[0]]['out'].append(edge[1])
        global_node_lst[edge[1]]['in'].append(edge[0])
    open_node_lst = copy.deepcopy(global_node_lst)
    print('global_node_lst:', global_node_lst)
    # 检查是否可以拓扑排序，即是否存在环
    while len(open_node_lst):
        print('open_node_lst:', open_node_lst)
        print('len(open_node_lst):', len(open_node_lst))
        find = False
        for nid, nvalue in open_node_lst.items():
            if len(nvalue['in']) == 0:
                find = True
                global_topo_nid_lst.append(nid)
                for tmp_nid, tmp_nvalue in open_node_lst.items():
                    for inid in tmp_nvalue['in']:
                        if inid == nid:
                            tmp_nvalue['in'].remove(inid)
                del open_node_lst[nid]
                break
        if not find:
            return False
    return True

# 生成模型代码
def gen_model_code(model_name, proj_id, dataset_name):
    model_code = global_import_packge.format(dataset_name)
    model_code += global_model_class
    model_code += 'class ' + str(model_name) + '(nn.Module):\n'\
                    +'\tdef __init__(self):\n'\
                    +'\t\tsuper('+str(model_name)+', self).__init__()\n'
    for layer_id in global_topo_nid_lst:
        layer = layer_table.query.get((layer_id, proj_id))
        module = module_def_table.query.get(int(layer.layer_module_id))        
        layer_param_list = pickle.loads(layer.layer_param_list)
        module_code = module.module_def_precode
        # 对代码模板进行参数替换
        for p in layer_param_list:
            module_code = re.sub(r'\$\d+', str(p), module_code, 1)
        # 生成一个block的代码
        model_code += '\t\tself.block' + layer_id + '=' + module_code + '\n'
    model_code += '\tdef forward(self, x):\n'
    print('global_topo_nid_lst:', global_topo_nid_lst)
    print('global_node_lst:', global_node_lst)
    for layer_id in global_topo_nid_lst:
        in_len = len(global_node_lst[layer_id]['in'])
        if in_len == 0:
            model_code += ('\t\tx' + layer_id + '=self.block' + layer_id + '(x)\n')
            continue
        elif in_len == 1:
            model_code += ('\t\tx' + layer_id + '=self.block' + layer_id + '(x' + global_node_lst[layer_id]['in'][0] +')\n')
            continue
        model_code += ('\t\taddfor_x'+layer_id+'=')
        first_add = True
        for in_layer_id in global_node_lst[layer_id]['in']:
            if first_add:
                first_add = False
                model_code += ('x'+in_layer_id) 
            else:
                model_code += ('+x'+in_layer_id)
        model_code += '\n'
        model_code += '\t\tx'+layer_id+'self.block'+layer_id+'(addfor_x'+layer_id+')\n'
    model_code += '\t\treturn x'+global_topo_nid_lst[-1] + '\n'
    return model_code

# 生成训练及测试代码
def gen_train_code(project_id, dataset_name):
    proj = project_table.query.get(project_id)
    proj_output = proj.project_outpath
    # project_superparam_id = proj.project_superparam_id
    # superparam = project_superparam_table.query.get(project_superparam_id)
    # batch_size = superparam.superparam_batchsize
    # epoch = superparam.superparam_epoch
    # lr = superparam.superparam_learnrate
    # optimizer = superparam.superparam_optim
    # lossfn = "CrossEntropyLoss" if superparam.superparam_lossfn == "CE" else "BCELoss"
    batch_size = 128
    epoch = 20
    lr = 0.001
    optimizer = 'Adam'
    lossfn = 'CrossEntropyLoss()'
    

    dataset_name = 'mnist'
    file_output = open(proj_output+"/train.py","w")
    file_output.write(global_import_packge.format(dataset_name))
    file_output.write("from model import *\n")
    file_output.write(global_batch_size.format(batch_size,batch_size))
    if dataset_name == "mnist":
        file_output.write(global_deal_data.format("mnist.MNIST","mnist.MNIST"))
    elif dataset_name == "cifar10":
        file_output.write(global_deal_data.format("cifar10.CIFAR10","cifar10.CIFAR10"))
    file_output.write(global_train_test_code.format(epoch,lossfn,lr,optimizer))
    file_output.write(global_train_test_code_print)
    file_output.write(global_loss_visualize.format(proj_output+"/pic/loss.jpg"))
    file_output.write(global_acc_visualize.format(proj_output+"/pic/acc.jpg"))
    file_output.close()

# 主要函数：生成代码
def gen_code(project_id):
    # 1. import code 
    # 2. modol code
    # 3. train && test code

    # dataset_id = proj.project_dataset_id
    # dataset = dataset_table.query.get(dataset_id)
    # dataset_name = dataset.dataset_name
    dataset_name = 'mnist'

    #生成模型代码文件
    proj = project_table.query.get(project_id)
    proj_output = proj.project_outpath
    model_file_path = proj_output+"/model.py"
    model_output = open(model_file_path,"w")
    if not check_structure(project_id):
        return False
    model_name = "myModel"
    model_code = gen_model_code(model_name, project_id, dataset_name)
    model_output.write(model_code)
    model_output.close()
    print("Genarate model code success!!!!\n")

    #生成训练代码文件：
    gen_train_code(project_id, dataset_name)
    print("Genarate train code success!!!!\n")

    return True


