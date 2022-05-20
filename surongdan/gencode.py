import re
from surongdan.extensions import db
from surongdan.models import module_def_table, project_table,project_superparam_table,dataset_table

global_import_packge = "import time\n\
import numpy as np\n\
from torchvision import transforms\n\
from torchvision.datasets import {0}\n\
from torch.utils.data import DataLoader\n\
import matplotlib.pyplot as plt\n\
import torch.nn as nn\n\
import torch.optim as optim\n"

global_batch_size = "train_batch_size = {0}\n\
                    test_batch_size = {1}"

global_deal_data = "transform = transforms.Compose([transforms.ToTensor(),transforms.Normalize([0.5],[0.5])])\n\
                    data_train = {0}('~/data/', train=True, transform=transform,target_transform=None, download=False)\n\
                    data_test  = {1}('~/data/', train=False, transform=transform,target_transform=None, download=False)\n\
                    train_loader = DataLoader(data_train, batch_size=train_batch_size, shuffle=True)\n\
                    test_loader = DataLoader(data_test,batch_size=test_batch_size,shuffle=True)\n\
                    "

global_train_test_code = "model = CNN()\n\
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
                \tprint(\'epoch:{},Train Loss:{:.4f},Train Acc:{:.4f},\',\'Test Loss:{:.4f},Test Acc:{:.4f}\'.format(epoch, train_loss / len(train_loader),train_acc / len(train_loader),eval_loss / len(test_loader),eval_acc / len(test_loader)))\n\
                \tstop_time = time.time()\n\
                \tprint(\"time is:{:.4f}s\".format(stop_time-start_time))\n\
                print(\"end training.\")\n\
                "

global_loss_visualize = "plt.figure()\n\
                    plt.title(\"loss\")\n\
                    plt.plot(np.arange(len(train_losses)), train_losses)\n\
                    plt.plot(np.arange(len(eval_losses)), eval_losses)\n\
                    plt.savefig(\"{0}\")\n\
                    "

global_acc_visualize = "plt.figure()\n\
                    plt.title(\"acc\")\n\
                    plt.plot(np.arange(len(train_acces)), train_acces)\n\
                    plt.plot(np.arange(len(eval_acces)), eval_acces)\n\
                    plt.savefig(\"{0}\")\n\
                    "


# 检查网络结构
def check_structure(project_id):    
    pass

# 生成模型代码
def gen_modol_code(project_id):
    pass

# 生成训练及测试代码
def gen_train_code(project_id):
    proj = project_table.query.get(project_id)
    proj_output = proj.project_outpath
    project_superparam_id = proj.project_superparam_id
    superparam = project_superparam_table.query.get(project_superparam_id)
    batch_size = superparam.superparam_batchsize
    epoch = superparam.superparam_epoch
    lr = superparam.superparam_learnrate
    optimizer = superparam.superparam_optim
    lossfn = "CrossEntropyLoss" if superparam.superparam_lossfn == "CE" else "BCELoss"
    dataset_id = proj.project_dataset_id
    dataset = dataset_table.query.get(dataset_id)
    dataset_name = dataset.dataset_name
    file_output = open(proj_output+"/model.py","w")
    file_output.write(global_import_packge.format(dataset_name))
    file_output.write(global_batch_size.format(batch_size,batch_size))
    if dataset_name == "mnist":
        file_output.write(global_deal_data.format("mnist.MNIST","mnist.MNIST"))
    elif dataset_name == "cifar10":
        file_output.write(global_deal_data.format("cifar10.CIFAR10","cifar10.CIFAR10"))
    file_output.write(global_train_test_code.format(epoch,lossfn,lr,optimizer))
    file_output.write(global_loss_visualize.format(proj_output+"/pic/loss.jpg"))
    file_output.write(global_acc_visualize.format(proj_output+"/pic/acc.jpg"))
    file_output.close()

# 主要函数：生成代码
def gen_code(project_id):
    # 1. import code 
    # 2. modol code
    # 3. train && test code
    pass
